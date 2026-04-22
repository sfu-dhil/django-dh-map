
from django.db import models
from django.utils.safestring import mark_safe
from pathlib import Path
from polymorphic.models import PolymorphicModel
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToCover, ResizeToFit

from .fields import AsyncFFileField, AsyncImageFFileField
from .settings import MEDIA_ROOT_DIR, MEDIA_URL

class Map(PolymorphicModel):
    label = models.CharField()
    date_taken = models.DateField(null=True, blank=True)
    license = models.CharField(null=True,blank=True)
    published = models.BooleanField(verbose_name='Published?', default=False, db_index=True)
    position = models.PositiveIntegerField(default=0, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_map_map'
        verbose_name = 'Map'
        ordering = ['position']

    def __str__(self):
        return f'Map {self.label} ({self.pk})'

    def get_date_label(self):
        return self.date.format('%Y', '%Y-%m', '%Y-%m-%d') if self.date else None

class AbstractImageMap(Map):
    class TileImageFormat(models.TextChoices):
        AVIF = 'avif', 'avif'
        WEBP = 'webp', 'webp'
        PNG = 'png', 'png'

    image = AsyncImageFFileField(
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
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(1920, 1080)],
        format='JPEG',
        options={'quality': 80},
    )

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

    def has_image(self):
        return bool(self.image.name) and self.image.storage.exists(self.image.name)

    def has_tiles(self):
        return bool(self.tiles_dir) and Path(self.tiles_dir).exists() and Path(self.tiles_dir).is_dir() and len(list(Path(self.tiles_dir).iterdir())) > 0

    def get_tiles_media_path(self):
        return Path(MEDIA_URL) / Path(self.tiles_dir).relative_to(MEDIA_ROOT_DIR) if self.tiles_dir else None

class OverheadImageMap(AbstractImageMap):
    # relationships

    class Meta:
        db_table = 'django_dh_map_overhead_map'
        verbose_name = 'Overhead Image Map'

    def __str__(self):
        return f'Overhead Image Map: {self.label}'


class PanoramaImageMap(AbstractImageMap):
    cube_size = models.IntegerField(null=True, blank=True)

    # relationships

    class Meta:
        db_table = 'django_dh_map_panorama_map'
        verbose_name = 'Panorama Image Map'

    def __str__(self):
        return f'Panorama Image Map: {self.label}'

class ContentItem(PolymorphicModel):
    # relationships
    # content_blocks via the ContentBlock Model

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_dh_map_ci'
        verbose_name = 'Content Item'

    def __str__(self):
        return f'Content Item: {self.pk}'

class InfoPage(ContentItem):
    title = models.CharField()
    published = models.BooleanField(verbose_name='Published?', default=False, db_index=True)
    position = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = 'django_dh_map_ci_info_page'
        verbose_name = 'Info Page'
        ordering = ['position']

    def __str__(self):
        return f'{self.title}'

class ContentBlock(PolymorphicModel):
    position = models.PositiveIntegerField(default=0, db_index=True)

    # relationships
    content_item = models.ForeignKey(
        ContentItem,
        related_name='content_blocks',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'django_dh_map_cb'
        verbose_name = 'Content Block'
        ordering = ['position', 'id']

class ContentBlockRichText(ContentBlock):
    content = models.TextField()

    class Meta:
        db_table = 'django_dh_map_cb_rich_text'
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
#     options={'quality': 90},
# )
# low_resolution = ImageSpecField(
#     source='original',
#     processors=[ResizeToFit(1280, 720)],
#     format='AVIF',
#     options={'quality': 80},
# )
class ContentBlockImage(ContentBlock):
    # fields
    name = models.CharField(blank=True, null=True)
    original = AsyncImageFFileField(
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
        options={'quality': 90},
    )
    thumbnail = ImageSpecField(
        source='original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 80},
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
    # content_item via ContentItem Model

    class Meta:
        db_table = 'django_dh_map_cb_image'
        verbose_name = 'Image'
        ordering = ['position']

    def __str__(self):
        if self.name:
            return self.name
        return self.original.name if self.original else super().__str__()


class ContentBlockImageGallery(ContentBlock):
    # relationships
    # content_item via ContentItem Model
    # images via the ContentBlockImageGalleryImage Model

    class Meta:
        db_table = 'django_dh_map_cb_image_gallery'
        verbose_name = 'Image Gallery'
        ordering = ['position']


class ContentBlockImageGalleryImage(models.Model):
    # fields
    position = models.PositiveIntegerField(default=0, db_index=True)
    name = models.CharField(blank=True, null=True)
    original = AsyncImageFFileField(
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
        options={'quality': 90},
    )
    thumbnail = ImageSpecField(
        source='original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 80},
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

    class Meta:
        db_table = 'django_dh_map_cb_image_gallery_image'
        verbose_name = 'Image Gallery Image'
        ordering = ['position']

class ContentBlockImageBeforeAndAfter(ContentBlock):
    # fields
    before_name = models.CharField(verbose_name='Name', blank=True, null=True)
    before_original = AsyncImageFFileField(
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
        options={'quality': 90},
    )
    before_thumbnail = ImageSpecField(
        source='before_original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 80},
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
    after_original = AsyncImageFFileField(
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
        options={'quality': 90},
    )
    after_thumbnail = ImageSpecField(
        source='after_original',
        processors=[ResizeToFill(320, 200)],
        format='AVIF',
        options={'quality': 80},
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

    # relationships
    # content_item via ContentItem Model

    class Meta:
        db_table = 'django_dh_map_cb_image_before_and_after'
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
        db_table = 'django_dh_map_cb_video'
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

    # relationships
    # content_item via ContentItem Model

    class Meta:
        db_table = 'django_dh_map_cb_audio'
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