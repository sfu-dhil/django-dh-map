from django_rq import enqueue
from pathlib import Path
from django.db.models.signals import post_delete, post_init, pre_save, post_save
from django.dispatch import receiver

from .models import OverheadImageMap, PanoramaImageMap, ContentBlockVideo, ContentBlockAudio
from .helpers import cleanup_directory
from .tasks import task_overhead_map_tiles_generator, task_panorama_map_tiles_generator, \
    task_video_stream_generator, task_video_snapshot_generator, task_video_thumbnails_vtt_generator, \
    task_audio_stream_generator

@receiver(post_init, sender=OverheadImageMap)
@receiver(post_init, sender=PanoramaImageMap)
def map_post_init(sender, instance, **kwargs):
    instance.old_image_path = instance.image.path if instance.has_image() else None

@receiver(post_delete, sender=OverheadImageMap)
@receiver(post_delete, sender=PanoramaImageMap)
def map_post_delete(sender, instance, **kwargs):
    tiles_dir = Path(instance.tiles_dir) if instance.tiles_dir else None
    cleanup_directory(tiles_dir)

@receiver(post_save, sender=OverheadImageMap)
@receiver(post_save, sender=PanoramaImageMap)
def map_post_save(sender, instance, **kwargs):
    image_path = instance.image.path if instance.has_image() else None
    has_new_image = image_path and image_path != instance.old_image_path

    if has_new_image:
        if isinstance(instance, OverheadImageMap):
            enqueue(task_overhead_map_tiles_generator, instance.pk)
        elif isinstance(instance, PanoramaImageMap):
            enqueue(task_panorama_map_tiles_generator, instance.pk)

@receiver(post_init, sender=ContentBlockVideo)
def video_post_init(sender, instance, **kwargs):
    instance.old_original_path = instance.original.path if instance.has_original() else None

@receiver(post_delete, sender=ContentBlockVideo)
def video_post_delete(sender, instance, **kwargs):
    video_dir = Path(instance.video_dir) if instance.video_dir else None
    cleanup_directory(video_dir)

@receiver(post_save, sender=ContentBlockVideo)
def video_post_save(sender, instance, **kwargs):
    original_path = instance.original.path if instance.has_original() else None
    has_new_video = original_path and original_path != instance.old_original_path

    if has_new_video:
        enqueue(task_video_snapshot_generator, instance.pk)
        enqueue(task_video_stream_generator, instance.pk)
        enqueue(task_video_thumbnails_vtt_generator, instance.pk)

@receiver(post_init, sender=ContentBlockAudio)
def audio_post_init(sender, instance, **kwargs):
    instance.old_original_path = instance.original.path if instance.has_original() else None

@receiver(post_delete, sender=ContentBlockAudio)
def audio_post_delete(sender, instance, **kwargs):
    audio_dir = Path(instance.audio_dir) if instance.audio_dir else None
    cleanup_directory(audio_dir)

@receiver(post_save, sender=ContentBlockAudio)
def audio_post_save(sender, instance, **kwargs):
    original_path = instance.original.path if instance.has_original() else None
    has_new_audio = original_path and original_path != instance.old_original_path

    if has_new_audio:
        enqueue(task_audio_stream_generator, instance.pk)