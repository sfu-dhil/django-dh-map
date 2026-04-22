
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django_rq import enqueue
from django.contrib import messages
from django.forms import widgets
from tinymce.widgets import TinyMCE
from js_asset import JS
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, \
    PolymorphicChildModelFilter
from nested_admin.nested import NestedModelAdmin, NestedStackedInline
from nested_admin.polymorphic import NestedPolymorphicModelAdmin, NestedStackedPolymorphicInline

from .tasks import task_overhead_map_tiles_generator, task_panorama_map_tiles_generator, \
    task_video_stream_generator, task_video_snapshot_generator, task_video_thumbnails_vtt_generator, \
    task_audio_stream_generator
from .helpers import get_success_failure_status_tick
from .models import Map, OverheadImageMap, PanoramaImageMap, AbstractImageMap, \
    InfoPage, ContentBlock, ContentBlockRichText, ContentBlockImage, ContentBlockImageGallery, \
    ContentBlockImageGalleryImage, ContentBlockImageBeforeAndAfter, ContentBlockVideo, ContentBlockAudio

def video_preview_app_tag(video, title, thumbnail, thumbnails_vtt):
    return f'<div class="admin-video-preview-app" data-video="{video.url}" data-title="{title}" data-thumbnail="{thumbnail.url if thumbnail else ''}" data-thumbnails-vtt="{thumbnails_vtt.url if thumbnails_vtt else ''}"></div>'

class DjangoDhMapAdminMixin:
  class Media:
    css = { 'all': ['django_dh_map/admin/dist/django_dh_map.css'] }
    js = [JS('django_dh_map/admin/dist/django_dh_map.js', {'type': 'module'})]

# based of SortableHiddenMixin
class SortableHiddenMixinTinyMceFix:
    sortable_field_name = "position"
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == self.sortable_field_name:
            kwargs["widget"] = widgets.HiddenInput(attrs={'class': '_sortable_field_'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

class AbstractImageMapChildAdmin(DjangoDhMapAdminMixin, PolymorphicChildModelAdmin):
    base_model = AbstractImageMap
    fields = ['label', 'date_taken', 'published', 'image', 'license']

@admin.register(OverheadImageMap)
class OverheadImageMapChildAdmin(AbstractImageMapChildAdmin):
    base_model = OverheadImageMap

@admin.register(PanoramaImageMap)
class PanoramaImageMapChildAdmin(AbstractImageMapChildAdmin):
    base_model = PanoramaImageMap

@admin.register(Map)
class MapParentAdmin(DjangoDhMapAdminMixin, PolymorphicParentModelAdmin):
    child_models = (OverheadImageMap, PanoramaImageMap)
    list_filter = [PolymorphicChildModelFilter]
    polymorphic_list = True
    ordering = ['id']

    list_display = ('id', '_type', 'label', 'date_taken', '_preview', '_status')
    list_display_links = ('id', '_type', 'label', 'date_taken')
    actions = ['reprocess_maps']

    @admin.action(description="(Re)process selected map(s)")
    def reprocess_maps(self, request, queryset):
        job_count = 0
        for map in queryset:
            if isinstance(map, OverheadImageMap) and map.has_image():
                # enqueue(task_overhead_map_tiles_generator, map.pk)
                task_overhead_map_tiles_generator(map.pk)
                job_count+=1
            elif isinstance(map, PanoramaImageMap) and map.has_image():
                enqueue(task_panorama_map_tiles_generator, map.pk)
                # task_panorama_map_tiles_generator(map.pk)
                job_count+=1
        self.message_user(request, f'Created {job_count} jobs.', messages.SUCCESS)

    def _type(self, obj):
        return obj._meta.verbose_name
    _type.short_description = 'Map Type'

    def _preview(self, obj):
        if isinstance(obj, PanoramaImageMap) and obj.tiles_dir:
            return mark_safe(f'<div class="panorama-map-preview-app" data-tiles-dir="{obj.get_tiles_media_path()}" data-tile-format="{obj.tile_format}" data-tile-size="{obj.tile_size}" data-cube-size="{obj.cube_size}" data-max-zoom="{obj.max_zoom}"></div>')
        elif isinstance(obj, OverheadImageMap) and obj.thumbnail:
            return mark_safe(f'<div class="overhead-map-preview-app" data-tiles-dir="{obj.get_tiles_media_path()}" data-tile-format="{obj.tile_format}" data-tile-size="{obj.tile_size}" data-width="{obj.width}" data-height="{obj.height}" data-min-zoom="{obj.min_zoom}" data-max-zoom="{obj.max_zoom}"></div>')
        return ''
    _preview.short_description = 'Preview'

    def _status(self, obj):
        if isinstance(obj, AbstractImageMap):
            return mark_safe(f'Map Tiles: {get_success_failure_status_tick(obj.has_tiles())}')
        return ''
    _status.short_description = "Status"

class ContentBlockInline(DjangoDhMapAdminMixin, SortableHiddenMixinTinyMceFix, NestedStackedPolymorphicInline):
    model = ContentBlock

    class ContentBlockRichTextInline(SortableHiddenMixinTinyMceFix, NestedStackedPolymorphicInline.Child):
        model = ContentBlockRichText
        formfield_overrides = { models.TextField: { 'widget': TinyMCE } }

    class ContentBlockImageInline(SortableHiddenMixinTinyMceFix, NestedStackedPolymorphicInline.Child):
        model = ContentBlockImage
        fields = [('_thumbnail_tag', 'original'), ('name', 'description', 'license'), 'position']
        readonly_fields = ['_thumbnail_tag']
        def _thumbnail_tag(self, obj):
            return mark_safe(f'<img class="admin-image-preview" src="{obj.thumbnail.url}" />') if obj.thumbnail else 'N/A'
        _thumbnail_tag.short_description = 'Preview'

    class ContentBlockImageGalleryInline(SortableHiddenMixinTinyMceFix, NestedStackedPolymorphicInline.Child):
        model = ContentBlockImageGallery
        fields = ['position']

        class ContentBlockImageGalleryImageInline(SortableHiddenMixinTinyMceFix, NestedStackedInline):
            model = ContentBlockImageGalleryImage
            min_num = 1
            extra = 0
            classes = ['collapse']
            fields = [('_thumbnail_tag', 'original'), ('name', 'description', 'license'), 'position']
            readonly_fields = ['_thumbnail_tag']
            def _thumbnail_tag(self, obj):
                return mark_safe(f'<img class="admin-image-preview" src="{obj.thumbnail.url}" />') if obj.thumbnail else 'N/A'
            _thumbnail_tag.short_description = 'Preview'

        inlines = [ContentBlockImageGalleryImageInline]

    class ContentBlockImageBeforeAndAfterInline(SortableHiddenMixinTinyMceFix, NestedStackedPolymorphicInline.Child):
        model = ContentBlockImageBeforeAndAfter
        fieldsets = (
            (None, { 'fields': [
                '_before_after_preview_tag', 'position'
            ], }),
            ('Before Image', { 'classes': ('collapse', 'expanded'), 'fields': [
                ('_before_thumbnail_tag', 'before_original'),
                ('before_name', 'before_description', 'before_license'),
            ], }),
            ('After Image', { 'classes': ('collapse', 'expanded'), 'fields': [
                ('_after_thumbnail_tag', 'after_original'),
                ('after_name', 'after_description', 'after_license'),
            ], }),
        )
        readonly_fields = ['_before_after_preview_tag', '_before_thumbnail_tag', '_after_thumbnail_tag']
        def _before_after_preview_tag(self, obj):
            return mark_safe(f'<div class="admin-before-after-preview-app" data-before="{obj.before_thumbnail.url}" data-after="{obj.after_thumbnail.url}"></div>') if obj.before_thumbnail and obj.after_thumbnail else 'N/A'
        _before_after_preview_tag.short_description = 'Preview'
        def _before_thumbnail_tag(self, obj):
            return mark_safe(f'<img class="admin-image-preview" src="{obj.before_thumbnail.url}" />') if obj.before_thumbnail else 'N/A'
        _before_thumbnail_tag.short_description = 'Preview'
        def _after_thumbnail_tag(self, obj):
            return mark_safe(f'<img class="admin-image-preview" src="{obj.after_thumbnail.url}" />') if obj.after_thumbnail else 'N/A'
        _after_thumbnail_tag.short_description = 'Preview'

    class ContentBlockVideoInline(SortableHiddenMixinTinyMceFix, NestedStackedPolymorphicInline.Child):
        model = ContentBlockVideo
        fields = [('_video_tag', 'original'), ('name', 'license'), 'position']
        readonly_fields = ['_video_tag']

        def _video_tag(self, obj):
            return mark_safe(video_preview_app_tag(obj.video, f'{obj}', obj.thumbnail, obj.thumbnails_vtt)) if obj.video else 'N/A'
        _video_tag.short_description = 'Preview'

    class ContentBlockAudioInline(SortableHiddenMixinTinyMceFix, NestedStackedPolymorphicInline.Child):
        model = ContentBlockAudio
        fields = [('_audio_tag', 'original'), ('name', 'license'), 'position']
        readonly_fields = ['_audio_tag']
        def _audio_tag(self, obj):
            return mark_safe(f'<audio src="{obj.audio.url}" controls preload="metadata" />') if obj.audio else 'N/A'
        _audio_tag.short_description = 'Preview'

    child_inlines = (
        ContentBlockRichTextInline,
        ContentBlockImageInline,
        ContentBlockImageGalleryInline,
        ContentBlockImageBeforeAndAfterInline,
        ContentBlockVideoInline,
        ContentBlockAudioInline,
    )

@admin.register(ContentBlockVideo)
class ContentBlockVideoAdmin(DjangoDhMapAdminMixin, PolymorphicChildModelAdmin):
    base_model = ContentBlockVideo
    fields = [('_video_tag', 'original'), ('name', 'license')]
    readonly_fields = ['_video_tag']
    show_in_index = True
    list_display = ('id', '_name', '_status')
    list_display_links = ('id', '_name')
    ordering = ['id']
    actions = ['reprocess_snapshot', 'reprocess_video_stream', 'reprocess_thumbnails_vtt']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _name(self, obj):
        return f'{obj}'
    _name.short_description = 'Name'

    def _status(self, obj):
        return mark_safe(f'''
            {get_success_failure_status_tick(obj.has_video())} Streamable<br />
            {get_success_failure_status_tick(obj.has_snapshot())} Poster Image<br />
            {get_success_failure_status_tick(obj.has_thumbnails_vtt())} Preview Thumbnails
        ''')
    _status.short_description = 'Status'

    def _video_tag(self, obj):
        return mark_safe(video_preview_app_tag(obj.video, f'{obj}', obj.thumbnail, obj.thumbnails_vtt)) if obj.video else 'N/A'
    _video_tag.short_description = 'Preview'

    @admin.action(description="(Re)process poster images for selected video(s)")
    def reprocess_snapshot(self, request, queryset):
        job_count = 0
        for video in queryset:
            enqueue(task_video_snapshot_generator, video.pk)
            # task_video_snapshot_generator(video.pk)
            job_count+=1
        self.message_user(request, f'Created {job_count} jobs.', messages.SUCCESS)

    @admin.action(description="(Re)process video stream for selected video(s)")
    def reprocess_video_stream(self, request, queryset):
        job_count = 0
        for video in queryset:
            enqueue(task_video_stream_generator, video.pk)
            # task_video_stream_generator(video.pk)
            job_count+=1
        self.message_user(request, f'Created {job_count} jobs.', messages.SUCCESS)

    @admin.action(description="(Re)process preview thumbnails for selected video(s)")
    def reprocess_thumbnails_vtt(self, request, queryset):
        job_count = 0
        for video in queryset:
            enqueue(task_video_thumbnails_vtt_generator, video.pk)
            # task_video_thumbnails_vtt_generator(video.pk)
            job_count+=1
        self.message_user(request, f'Created {job_count} jobs.', messages.SUCCESS)

@admin.register(ContentBlockAudio)
class ContentBlockAudioAdmin(DjangoDhMapAdminMixin, PolymorphicChildModelAdmin):
    base_model = ContentBlockAudio
    fields = [('_audio_tag', 'original'), ('name', 'license')]
    readonly_fields = ['_audio_tag']
    show_in_index = True
    list_display = ('id', '_name', '_status')
    list_display_links = ('id', '_name')
    ordering = ['id']
    actions = ['reprocess_audio_stream']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _name(self, obj):
        return f'{obj}'
    _name.short_description = 'Name'

    def _status(self, obj):
        return mark_safe(f'''
            {get_success_failure_status_tick(obj.has_audio())} Streamable
        ''')
    _status.short_description = 'Status'

    def _audio_tag(self, obj):
        return mark_safe(f'<audio src="{obj.audio.url}" controls preload="metadata" />') if obj.audio else 'N/A'
    _audio_tag.short_description = 'Preview'

    @admin.action(description="(Re)process audio stream for selected audio(s)")
    def reprocess_audio_stream(self, request, queryset):
        job_count = 0
        for audio in queryset:
            # enqueue(task_audio_stream_generator, audio.pk)
            task_audio_stream_generator(audio.pk)
            job_count+=1
        self.message_user(request, f'Created {job_count} jobs.', messages.SUCCESS)

@admin.register(InfoPage)
class InfoPageAdmin(DjangoDhMapAdminMixin, NestedPolymorphicModelAdmin):
    list_display = ('id', 'title', '_status')
    list_display_links = ('id', 'title')
    ordering = ['id']
    fields = ['title', 'published']

    inlines = [
        ContentBlockInline,
    ]

    def _status(self, obj):
        video_status = [
            f'- {get_success_failure_status_tick(video.has_video())} Streamable | {get_success_failure_status_tick(video.has_snapshot())} Poster Image | {get_success_failure_status_tick(video.has_thumbnails_vtt())} Preview Thumbnails | {video.name if video.name else video.original.name}' for video in obj.content_blocks.instance_of(ContentBlockVideo).all()
        ]
        video_status_str = '' if len(video_status) == 0 else 'Videos: <br />' + '<br />'.join(video_status) + '<br />'
        audio_status = [
            f'- {get_success_failure_status_tick(audio.has_audio())} Streamable | {audio.name if audio.name else audio.original.name}' for audio in obj.content_blocks.instance_of(ContentBlockAudio).all()
        ]
        audio_status_str = '' if len(audio_status) == 0 else 'Audio: <br />' + '<br />'.join(audio_status) + '<br />'

        return mark_safe(f'''
            {get_success_failure_status_tick(obj.published)} Published<br />
            {video_status_str}
            {audio_status_str}
        ''')
    _status.short_description = "Status"