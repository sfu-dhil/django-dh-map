
from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.gis.db.models.fields import MultiPointField, PointField
from pathlib import Path
from polymorphic.models import PolymorphicModel
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit
from django_jsonform.models.fields import JSONField

from .fields import AsyncFFileField, ImageFFileField
from .settings import MEDIA_ROOT_DIR, MEDIA_URL, \
    DH_MAP_CI_FEATURE_PROPERTIES_SCHEMA

class Map(PolymorphicModel):
    class SpacialReferenceIdentifier(models.IntegerChoices):
        FLAT_CARTESIAN = 0, 'Flat, Cartesian coordinate system (SRID 0)'
        WGS_84 = 4326, 'World Geodetic System (WGS84 / SRID 4326)'
        WEB_MERCATOR = 3857, 'Web Mercator (SRID 3857)'
        # add more supported SRIDs over time

    label = models.CharField()
    date_taken = models.DateField(null=True, blank=True)
    license = models.CharField(null=True,blank=True)
    published = models.BooleanField(verbose_name='Published?', default=False, db_index=True)
    position = models.IntegerField(default=0, db_index=True)

    data_srid = models.PositiveIntegerField(
        verbose_name='GeoJson Projection Spacial Reference Identifier (SRID)',
        choices=SpacialReferenceIdentifier.choices,
        default=SpacialReferenceIdentifier.WGS_84
    )
    feature_srid = models.PositiveIntegerField(
        verbose_name='Map Projection Spacial Reference Identifier (SRID)',
        choices=SpacialReferenceIdentifier.choices,
        default=SpacialReferenceIdentifier.WEB_MERCATOR
    )
    properties = models.JSONField(null=True, blank=True, default=dict)

    # relationships
    # features via the Feature Model
    # map_geojson via the MapGeoJson Model
    map_transitions = models.ManyToManyField(
        'self',
        through='MapGeoJsonTransition',
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_map'
        verbose_name = 'Map'
        ordering = ['position']

    def save(self, *args, **kwargs):
        if not self.pk and not self.position:
            self.position = (Map.objects.aggregate(models.Max('position'))['position__max'] or 0 ) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Map {self.label} ({self.pk})'

    def get_date_label(self):
        return self.date.format('%Y', '%Y-%m', '%Y-%m-%d') if self.date else None

class AbstractExternalServiceMap(Map):
    url = models.CharField()
    min_zoom = models.IntegerField(null=True, blank=True)
    max_zoom = models.IntegerField(null=True, blank=True)
    attributions = models.CharField(blank=True, null=True)

    class Meta:
        abstract = True

class XyzMap(AbstractExternalServiceMap):
    class Meta:
        db_table = 'django_dh_map_xyz'
        verbose_name = 'XYZ Map'

    def __str__(self):
        return f'XYZ Map: {self.label}'

class AbstractImageMap(Map):
    class TileImageFormat(models.TextChoices):
        AVIF = 'avif', 'avif'
        WEBP = 'webp', 'webp'
        PNG = 'png', 'png'

    image = ImageFFileField(
        verbose_name='High Resolution Map Image',
        max_length=255,
        upload_to='maps/',
        width_field='width',
        height_field='height',
        help_text=mark_safe('Please use a high resolution image.<br/>PNG or TIFF are recommended.<br/>JPEG, PNG, WEBP, AVIF, and TIFF are allowed.'),
        allowd_types=['jpeg', 'png', 'webp', 'avif', 'tiff'],
    )
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    tiles_dir = models.FilePathField(
        max_length=255,
        null=True,
        blank=True,
        path=(MEDIA_ROOT_DIR / 'maps/'),
        allow_folders=True,
        allow_files=False,
        recursive=False,
        match='(overhead|panorama)_.*$',
    )
    tile_size = models.IntegerField(null=True, blank=True)
    tile_format = models.CharField(choices=TileImageFormat.choices, null=True, blank=True)
    min_zoom = models.IntegerField(null=True, blank=True)
    max_zoom = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Assume all image maps are generic flat by default
        if not self.pk:
            self.data_srid = Map.SpacialReferenceIdentifier.FLAT_CARTESIAN
            self.feature_srid = Map.SpacialReferenceIdentifier.FLAT_CARTESIAN

    def has_image(self):
        return bool(self.image.name) and self.image.storage.exists(self.image.name)

    def has_tiles(self):
        return bool(self.tiles_dir) and Path(self.tiles_dir).exists() and Path(self.tiles_dir).is_dir() and len(list(Path(self.tiles_dir).iterdir())) > 0

    def get_tiles_media_path(self):
        return Path(MEDIA_URL) / Path(self.tiles_dir).relative_to(MEDIA_ROOT_DIR) if self.tiles_dir else None

class OverheadImageMap(AbstractImageMap):
    class Meta:
        db_table = 'django_dh_map_overhead'
        verbose_name = 'Overhead Image Map'

    def __str__(self):
        return f'Overhead Image Map: {self.label}'


class PanoramaImageMap(AbstractImageMap):
    cube_size = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'django_dh_map_panorama'
        verbose_name = 'Panorama Image Map'

    def __str__(self):
        return f'Panorama Image Map: {self.label}'

class ContentItem(PolymorphicModel):
    # relationships
    # content_blocks via the ContentBlock Model

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_ci'
        verbose_name = 'Content Item'
        ordering = ['id']

    def __str__(self):
        return f'Content Item: {self.pk}'

class InfoPage(ContentItem):
    title = models.CharField()
    published = models.BooleanField(verbose_name='Published?', default=False, db_index=True)
    position = models.IntegerField(default=0, db_index=True)

    class Meta:
        db_table = 'django_dh_ci_info_page'
        verbose_name = 'Info Page'
        ordering = ['position']

    def save(self, *args, **kwargs):
        if not self.pk and not self.position:
            self.position = (Map.objects.aggregate(models.Max('position'))['position__max'] or 0 ) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'

class Feature(ContentItem):
    title = models.CharField()
    published = models.BooleanField(verbose_name='Published?', default=False, db_index=True)
    properties = JSONField(schema=DH_MAP_CI_FEATURE_PROPERTIES_SCHEMA, null=True, blank=True, default=dict)

    # relationships
    # map_features via the MapGeoJson Model
    # icon via Icon Model
    maps = models.ManyToManyField(
        Map,
        through='MapGeoJsonFeature',
        related_name='features',
    )

    class Meta:
        db_table = 'django_dh_ci_feature'
        verbose_name = 'Feature'

    def __str__(self):
        return f'{self.title}'

class MapGeoJson(PolymorphicModel):
    # relationships
    map = models.ForeignKey(
        Map,
        related_name='map_geojson',
        on_delete=models.CASCADE,
    )
    extra = models.JSONField(default=dict)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_geojson'
        verbose_name = 'GeoJson'

class MapGeoJsonFeature(MapGeoJson):
    geom_points = MultiPointField(blank=True, null=True)

    # relationships
    feature = models.ForeignKey(
        Feature,
        related_name='map_geojson',
        on_delete=models.CASCADE,
    )
    class Meta:
        db_table = 'django_dh_geojson_feature'
        verbose_name = 'GeoJson Feature'

class MapGeoJsonTransition(MapGeoJson):
    geom_points = MultiPointField(blank=True, null=True)

    # relationships
    destination_map = models.ForeignKey(
        Map,
        related_name='destination_map_geojson_transition',
        on_delete=models.CASCADE,
    )
    class Meta:
        db_table = 'django_dh_geojson_transition'
        verbose_name = 'GeoJson Transition'

class MapGeoJsonLabel(MapGeoJson):
    label = models.TextField()
    geom_point = PointField(blank=True, null=True)

    class Meta:
        db_table = 'django_dh_geojson_label'
        verbose_name = 'GeoJson Label'

class ContentBlock(PolymorphicModel):
    position = models.IntegerField(default=0, db_index=True)

    # relationships
    content_item = models.ForeignKey(
        ContentItem,
        related_name='content_blocks',
        on_delete=models.CASCADE,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_cb'
        verbose_name = 'Content Block'
        ordering = ['position', 'id']

    def save(self, *args, **kwargs):
        if not self.pk and not self.position:
            self.position = (Map.objects.aggregate(models.Max('position'))['position__max'] or 0 ) + 1
        super().save(*args, **kwargs)

class ContentBlockRichText(ContentBlock):
    content = models.TextField()

    class Meta:
        db_table = 'django_dh_cb_rich_text'
        verbose_name = 'Rich Text'
        ordering = ['position']

# high_resolution = ImageSpecField(
#     source='original',
#     processors=[ResizeToFit(4096, 2160)],
#     format='AVIF',
#     options={'quality': 100},
# )
# medium_resolution = ImageSpecField(
#     source='original',
#     processors=[ResizeToFit(1920, 1080)],
#     format='AVIF',
#     options={'quality': 95},
# )
# low_resolution = ImageSpecField(
#     source='original',
#     processors=[ResizeToFit(1280, 720)],
#     format='AVIF',
#     options={'quality': 90},
# )
class ContentBlockImage(ContentBlock):
    # fields
    name = models.CharField(blank=True, null=True)
    original = ImageFFileField(
        verbose_name='High Resolution Image',
        max_length=255,
        upload_to='images/',
        help_text=mark_safe('Please use a high resolution image.<br/>JPEG, PNG, WEBP, and AVIF are allowed.'),
        allowd_types=['jpeg', 'png', 'webp', 'avif'],
    )
    web_resolution = ImageSpecField(
        source='original',
        processors=[ResizeToFit(1920, 1080)],
        format='AVIF',
        options={'quality': 95},
    )
    thumbnail = ImageSpecField(
        source='original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 90},
    )
    description = models.CharField(
        null=True,
        blank=True,
        help_text='Description of the image for accessibility.',
    )
    license = models.CharField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'django_dh_cb_image'
        verbose_name = 'Image'
        ordering = ['position']

    def __str__(self):
        if self.name:
            return self.name
        return self.original.name if self.original else super().__str__()


class ContentBlockImageGallery(ContentBlock):
    # relationships
    # images via the ContentBlockImageGalleryImage Model

    class Meta:
        db_table = 'django_dh_cb_image_gallery'
        verbose_name = 'Image Gallery'
        ordering = ['position']


class ContentBlockImageGalleryImage(models.Model):
    # fields
    position = models.IntegerField(default=0, db_index=True)
    name = models.CharField(blank=True, null=True)
    original = ImageFFileField(
        verbose_name='High Resolution Image',
        max_length=255,
        upload_to='images/',
        help_text=mark_safe('Please use a high resolution image.<br/>JPEG, PNG, WEBP, and AVIF are allowed.'),
        allowd_types=['jpeg', 'png', 'webp', 'avif'],
    )
    web_resolution = ImageSpecField(
        source='original',
        processors=[ResizeToFit(1920, 1080)],
        format='AVIF',
        options={'quality': 95},
    )
    thumbnail = ImageSpecField(
        source='original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 90},
    )
    description = models.CharField(
        null=True,
        blank=True,
        help_text='Description of the image for accessibility.',
    )
    license = models.CharField(
        null=True,
        blank=True,
    )

    # relationships
    gallery = models.ForeignKey(
        ContentBlockImageGallery,
        related_name='images',
        on_delete=models.CASCADE,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_cb_image_gallery_image'
        verbose_name = 'Image Gallery Image'
        ordering = ['position']

    def save(self, *args, **kwargs):
        if not self.pk and not self.position:
            self.position = (Map.objects.aggregate(models.Max('position'))['position__max'] or 0 ) + 1
        super().save(*args, **kwargs)

class ContentBlockImageBeforeAndAfter(ContentBlock):
    # fields
    caption = models.CharField(
        null=True,
        blank=True,
        help_text='Caption for the before and after images.',
    )
    before_name = models.CharField(verbose_name='Name', blank=True, null=True)
    before_original = ImageFFileField(
        verbose_name='High Resolution Image',
        max_length=255,
        upload_to='images/',
        help_text=mark_safe('Please use a high resolution image.<br/>JPEG, PNG, WEBP, and AVIF are allowed.'),
        allowd_types=['jpeg', 'png', 'webp', 'avif'],
    )
    before_web_resolution = ImageSpecField(
        source='before_original',
        processors=[ResizeToFit(1920, 1080)],
        format='AVIF',
        options={'quality': 95},
    )
    before_thumbnail = ImageSpecField(
        source='before_original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 90},
    )
    before_description = models.CharField(
        verbose_name='Description',
        null=True,
        blank=True,
        help_text='Description of the image for accessibility.',
    )
    before_license = models.CharField(
        verbose_name='License',
        null=True,
        blank=True,
    )
    after_name = models.CharField(verbose_name='Name', blank=True, null=True)
    after_original = ImageFFileField(
        verbose_name='High Resolution Image',
        max_length=255,
        upload_to='images/',
        help_text=mark_safe('Please use a high resolution image.<br/>JPEG, PNG, WEBP, and AVIF are allowed.'),
        allowd_types=['jpeg', 'png', 'webp', 'avif'],
    )
    after_web_resolution = ImageSpecField(
        source='after_original',
        processors=[ResizeToFit(1920, 1080)],
        format='AVIF',
        options={'quality': 95},
    )
    after_thumbnail = ImageSpecField(
        source='after_original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 90},
    )
    after_description = models.CharField(
        verbose_name='Description',
        null=True,
        blank=True,
        help_text='Description of the image for accessibility.',
    )
    after_license = models.CharField(
        verbose_name='License',
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'django_dh_cb_image_before_and_after'
        verbose_name = 'Image Before & After'
        ordering = ['position']


class ContentBlockVideo(ContentBlock):
    # fields
    name = models.CharField(blank=True, null=True)
    original = AsyncFFileField(
        verbose_name='High Resolution Video',
        max_length=255,
        upload_to='videos/',
        help_text=mark_safe('Please use a high resolution video.'),
        # allowd_types=['jpeg', 'png', 'webp', 'avif'],
    )
    video_dir = models.FilePathField(
        max_length=255,
        null=True,
        blank=True,
        path=(MEDIA_ROOT_DIR / 'videos/'),
        allow_folders=True,
        allow_files=False,
        recursive=False,
        match='video_.*$',
    )
    video = models.FileField(
        upload_to='videos/',
        null=True,
        blank=True,
    )
    snapshot = models.ImageField(
        upload_to='videos/',
        null=True,
        blank=True,
    )
    thumbnail = ImageSpecField(
        source='snapshot',
        processors=[ResizeToFit(1920, 1080)],
        format='AVIF',
        options={'quality': 90},
    )
    thumbnails_vtt = models.FileField(
        upload_to='videos/',
        null=True,
        blank=True,
    )
    license = models.CharField(
        null=True,
        blank=True,
    )

    # relationships
    # content_item via ContentItem Model

    class Meta:
        db_table = 'django_dh_cb_video'
        verbose_name = 'Video'
        ordering = ['position']

    def __str__(self):
        if self.name:
            return self.name
        return self.original.name if self.original else super().__str__()

    def has_original(self):
        return bool(self.original.name) and self.original.storage.exists(self.original.name)

    def has_video_dir(self):
        return bool(self.video_dir) and Path(self.video_dir).exists() and Path(self.video_dir).is_dir() and len(list(Path(self.video_dir).iterdir())) > 0

    def has_video(self):
        return bool(self.video.name) and self.video.storage.exists(self.video.name)

    def has_snapshot(self):
        return bool(self.snapshot.name) and self.snapshot.storage.exists(self.snapshot.name)

    def has_thumbnails_vtt(self):
        return bool(self.thumbnails_vtt.name) and self.thumbnails_vtt.storage.exists(self.thumbnails_vtt.name)

class ContentBlockAudio(ContentBlock):
    # fields
    name = models.CharField(blank=True, null=True)
    original = AsyncFFileField(
        verbose_name='High Quality Audio',
        max_length=255,
        upload_to='audio/',
        help_text=mark_safe('Please use a high quality audio.'),
        # allowd_types=['jpeg', 'png', 'webp', 'avif'],
    )
    audio_dir = models.FilePathField(
        max_length=255,
        null=True,
        blank=True,
        path=(MEDIA_ROOT_DIR / 'audio/'),
        allow_folders=True,
        allow_files=False,
        recursive=False,
        match='audio_.*$',
    )
    audio = models.FileField(
        upload_to='audio/',
        null=True,
        blank=True,
    )
    license = models.CharField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'django_dh_cb_audio'
        verbose_name = 'Audio'
        verbose_name_plural = 'Audio'
        ordering = ['position']

    def __str__(self):
        if self.name:
            return self.name
        return self.original.name if self.original else super().__str__()

    def has_original(self):
        return bool(self.original.name) and self.original.storage.exists(self.original.name)

    def has_audio_dir(self):
        return bool(self.audio_dir) and Path(self.audio_dir).exists() and Path(self.audio_dir).is_dir() and len(list(Path(self.audio_dir).iterdir())) > 0

    def has_audio(self):
        return bool(self.audio.name) and self.audio.storage.exists(self.audio.name)

class Icon(PolymorphicModel):
    # relationships
    feature = models.OneToOneField(
        Feature,
        related_name='icon',
        on_delete=models.CASCADE,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_icon'
        verbose_name = 'Icon'

class IconNumbered(Icon):
    number = models.IntegerField()

    class Meta:
        db_table = 'django_dh_icon_numbered'
        verbose_name = 'Numbered Icon'

# class IconFont(Icon):
#     class_value = models.CharField(
#         verbose_name='Bootstrap or FontAwesome Icon',
#         choices=FontIcon.choices,
#         help_text=mark_safe('Select a <u><a href="https://icons.getbootstrap.com/" target="_blank">Bootstrap</a></u> or <u><a href="https://fontawesome.com/search?ip=classic&ic=free-collection" target="_blank">Fontawesome Free</a></u> icon to use. Not all icons may be available.'),
#     )

#     class Meta:
#         db_table = 'django_dh_icon_font'
#         verbose_name = 'Font Icon'

class IconImage(Icon):
    THUMBNAIL_SIZE = 40
    original = ImageFFileField(
        verbose_name='High Resolution Image',
        max_length=255,
        upload_to='images/',
        help_text=mark_safe('Please use a high resolution image.<br/>JPEG, PNG, WEBP, and AVIF are allowed.'),
        allowd_types=['jpeg', 'png', 'webp', 'avif'],
    )
    thumbnail = ImageSpecField(
        source='original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 90},
    )
    icon_thumbnail = ImageSpecField(
        source='original',
        processors=[ResizeToFill(THUMBNAIL_SIZE, THUMBNAIL_SIZE)],
        format='AVIF',
        options={'quality': 90},
    )

    class Meta:
        db_table = 'django_dh_icon_image'
        verbose_name = 'Image Icon'