import math
import subprocess
import numpy as np
from natsort import natsorted
from tempfile import NamedTemporaryFile, TemporaryDirectory
from py360convert import e2c
from pathlib import Path
from PIL import Image
from .settings import MEDIA_ROOT_DIR, MEDIA_URL, \
    DH_MAPPING_OVERHEAD_TILE_SIZE, DH_MAPPING_PANORAMA_TILE_SIZE, \
    DH_MAPPING_FFMPEG, DH_MAPPING_VIDEO_RESOLUTIONS, \
    DH_MAPPING_VIDEO_SEGMENT_DURATION, DH_MAPPING_VIDEO_THUMBNAIL_INTERVAL
from django_rq import job

from .models import OverheadImageMap, PanoramaImageMap, ContentBlockVideo, ContentBlockAudio
from .helpers import cleanup_directory, chown_directory

@job('default', timeout=(60 * 15))
def task_overhead_map_tiles_generator(object_pk):
    map = OverheadImageMap.objects.get(pk=object_pk)
    if map.has_image():
        image_path = Path(map.image.path)
        original_img_file = Image.open(image_path.absolute())
        original_img_width, original_img_height = original_img_file.size

        tiles_dir = MEDIA_ROOT_DIR / 'maps' / f'overhead_{map.pk}'
        cleanup_directory(tiles_dir)
        tiles_dir.mkdir(parents=True, exist_ok=True)

        map.tiles_dir = tiles_dir
        map.tile_format = map.TileImageFormat.WEBP
        map.tile_size = min(DH_MAPPING_OVERHEAD_TILE_SIZE, original_img_width)
        map.min_zoom = 1
        map.max_zoom = int(math.ceil(math.log(float(original_img_width) / map.tile_size, 2)))

        try:
            gdal_raster_tile_call = f'gdal raster tile --tiling-scheme=raster --output-format=WEBP --webviewer=none --min-zoom={map.min_zoom} --max-zoom={map.max_zoom} --tile-size={map.tile_size} --add-alpha --input={image_path.absolute()} --output={tiles_dir.absolute()}'
            subprocess.run(
                gdal_raster_tile_call,
                shell=True, check=True, capture_output=True, timeout=(60 * 10)
            )
        except subprocess.CalledProcessError as e:
            if 'tile: Only Byte data type supported for WEBP.' in e.stderr.decode():
                # fix 16-bit issue
                map.tile_format = map.TileImageFormat.PNG
                subprocess.run(
                    gdal_raster_tile_call.replace('--output-format=WEBP', '--output-format=PNG'),
                    shell=True, check=True, capture_output=True, timeout=(60 * 10)
                )
            else:
                raise e

        chown_directory(tiles_dir)
        map.save()

# greatly inspired by https://github.com/mpetroff/pannellum/blob/master/utils/multires/generate.py
@job('default', timeout=(60 * 15))
def task_panorama_map_tiles_generator(object_pk):
    map = PanoramaImageMap.objects.get(pk=object_pk)
    if map.has_image():
        image_path = Path(map.image.path)
        original_img_file = Image.open(image_path.absolute())
        original_img_width, original_img_height = original_img_file.size

        tiles_dir = MEDIA_ROOT_DIR / 'maps' / f'panorama_{map.pk}'
        cleanup_directory(tiles_dir)
        tiles_dir.mkdir(parents=True, exist_ok=True)
        fallback_dir = tiles_dir / 'fallback'
        fallback_dir.mkdir(parents=True, exist_ok=True)

        cube_dict = e2c(np.array(original_img_file), face_w=(original_img_width // 4), cube_format='dict')

        map.tiles_dir = tiles_dir
        map.tile_format = map.TileImageFormat.AVIF
        HAOV = 360.0 # assume 360 panorama
        map.cube_size = 8 * int((360 / HAOV) * original_img_width / math.pi / 8)
        map.tile_size = min(DH_MAPPING_PANORAMA_TILE_SIZE, map.cube_size)
        map.min_zoom = 1
        map.max_zoom = int(math.ceil(math.log(float(map.cube_size) / map.tile_size, 2))) + 1
        if int(map.cube_size / 2**(map.max_zoom - 2)) == map.tile_size:
            map.max_zoom -= 1  # Handle edge case

        for face_name, face_img_array in cube_dict.items():
            face_path = fallback_dir / f'{face_name.lower()}.avif'
            face_img = Image.fromarray(face_img_array)
            face_img.save(face_path.absolute(), format='avif')

            current_size = map.cube_size
            for zoom_level in range(map.max_zoom, 0, -1):
                zoom_level_dir = tiles_dir / f'{zoom_level}'
                zoom_level_dir.mkdir(parents=True, exist_ok=True)
                face_img = face_img.resize([current_size, current_size], Image.Resampling.LANCZOS)
                num_tiles = int(math.ceil(float(current_size) / map.tile_size))
                for i in range(0, num_tiles):
                    for j in range(0, num_tiles):
                        tile_img_path = zoom_level_dir / f'{face_name.lower()}_{i}_{j}.avif'
                        tile_img = face_img.crop([
                            j * map.tile_size, # left
                            i * map.tile_size, # upper
                            min(j * map.tile_size + map.tile_size, current_size), # right
                            min(i * map.tile_size + map.tile_size, current_size)  # lower
                        ])
                        tile_img.save(tile_img_path)
                current_size = int(current_size / 2)

        chown_directory(tiles_dir)
        map.save()

@job('default', timeout=(60 * 5))
def task_video_snapshot_generator(object_pk):
    video = ContentBlockVideo.objects.get(pk=object_pk)

    if video.has_original():
        original_path = Path(video.original.path)

        video_dir = MEDIA_ROOT_DIR / 'videos' / f'video_{video.pk}'
        video_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = video_dir / 'snapshot.avif'
        if snapshot_path.exists() and snapshot_path.is_file():
            snapshot_path.unlink(missing_ok=True)

        # use ffmpeg to generate get an interesting snapshot within 500 frames
        subprocess.run(
            f'{DH_MAPPING_FFMPEG} -i {original_path.absolute()} -filter:v thumbnail=500 -frames:v 1 {snapshot_path.absolute()}',
            shell=True, check=True, capture_output=True, timeout=(60 * 1)
        )

        chown_directory(video_dir)
        video.video_dir = video_dir
        video.snapshot.name = f'{snapshot_path.relative_to(MEDIA_ROOT_DIR)}'
        video.save()

@job('default', timeout=(60 * 50))
def task_video_stream_generator(object_pk):
    video = ContentBlockVideo.objects.get(pk=object_pk)

    if video.has_original():
        original_path = Path(video.original.path)

        video_dir = MEDIA_ROOT_DIR / 'videos' / f'video_{video.pk}'
        video_stream_dir = video_dir / 'stream'
        cleanup_directory(video_stream_dir)
        video_stream_dir.mkdir(parents=True, exist_ok=True)
        dash_video_path = video_stream_dir / 'master.mpd'

        resolution_maps = []
        resolutions = []
        for index, resolution_dict in enumerate(DH_MAPPING_VIDEO_RESOLUTIONS):
            height = int(resolution_dict.get('height', 0))
            bitrate = int(resolution_dict.get('bitrate', 0))
            if height <= 0 or bitrate <= 0:
                raise ValueError(f'Invalid resolution: {resolution_dict}')
            width = int(height * 16 / 9)

            resolution_maps.append('-map 0:v')
            resolutions.append(f'-s:v:{index} {width}x{height} -b:v:{index} {bitrate}k')
        resolution_maps.append('-map 0:a') # audio map

        # use ffmpeg to generate dash and hls streams (multiple resolutions)
        subprocess.run(
f'''{DH_MAPPING_FFMPEG} -i {original_path.absolute()}
{' '.join(resolution_maps)}
{' '.join(resolutions)}
-c:a aac -b:a 256k
-c:v libsvtav1
-f dash
-adaptation_sets "id=0,streams=v id=1,streams=a"
-seg_duration {DH_MAPPING_VIDEO_SEGMENT_DURATION} -sc_threshold 0 -b_strategy 0 -g 100 -keyint_min 100
-use_timeline 1 -use_template 1 -hls_playlist 1
{dash_video_path.absolute()}'''.replace('\n', ' '),
            shell=True, check=True, capture_output=True, timeout=(60 * 45)
        )

        chown_directory(video_dir)
        video.video_dir = video_dir
        video.video.name = f'{dash_video_path.relative_to(MEDIA_ROOT_DIR)}'
        video.save()

@job('default', timeout=(60 * 15))
def task_video_thumbnails_vtt_generator(object_pk):
    video = ContentBlockVideo.objects.get(pk=object_pk)

    if video.has_original():
        original_path = Path(video.original.path)

        video_dir = MEDIA_ROOT_DIR / 'videos' / f'video_{video.pk}'
        video_dir.mkdir(parents=True, exist_ok=True)

        thumbnails_vtt_path = video_dir / 'thumbnails.vtt'
        if thumbnails_vtt_path.exists() and thumbnails_vtt_path.is_file():
            thumbnails_vtt_path.unlink(missing_ok=True)
        storyboard_path = video_dir / 'storyboard.avif'
        if storyboard_path.exists() and storyboard_path.is_file():
            storyboard_path.unlink(missing_ok=True)

        with TemporaryDirectory() as temp_dir:
            # use ffmpeg to generate get an interesting snapshot within 500 frames
            subprocess.run(
                f'{DH_MAPPING_FFMPEG} -i {original_path.absolute()} -filter:v fps=1/{DH_MAPPING_VIDEO_THUMBNAIL_INTERVAL},scale=256:144 {temp_dir}/storyboard_%d.jpg',
                shell=True, check=True, capture_output=True, timeout=(60 * 10)
            )

            temp_files = natsorted(list(Path(temp_dir).glob('*')))
            total_temp_files = len(temp_files)
            if total_temp_files > 0:
                with open(thumbnails_vtt_path.absolute(), 'w') as thumbnails_vtt_file:
                    thumbnails_vtt_file.write('WEBVTT\n\n')
                    width, height = 0, 0
                    with Image.open(temp_files[0].absolute()) as first_image_file:
                        width, height = first_image_file.width, first_image_file.height
                    total_width, total_height = width * (10 if total_temp_files >= 10 else total_temp_files), height * math.ceil(total_temp_files / 10.0)

                    storyboard_image = Image.new('RGBA', size=(total_width, total_height), color=(0, 0, 0, 0))
                    storyboard_image_url = Path(MEDIA_URL) / storyboard_path.relative_to(MEDIA_ROOT_DIR)

                    for index, temp_file in enumerate(temp_files):
                        with Image.open(temp_file.absolute()) as temp_image_file:
                            w_index = width * (index % 10)
                            h_index = height * math.floor(index / 10)
                            storyboard_image.paste(temp_image_file, box=(w_index, h_index))

                            start_time = index * DH_MAPPING_VIDEO_THUMBNAIL_INTERVAL
                            end_time = (index + 1) * DH_MAPPING_VIDEO_THUMBNAIL_INTERVAL
                            start_time_str = f'{start_time//3600:02d}:{(start_time//60)%60:02d}:{start_time%60:06.3f}'
                            end_time_str = f'{end_time//3600:02d}:{(end_time//60)%60:02d}:{end_time%60:06.3f}'
                            thumbnails_vtt_file.write(f'{start_time_str} --> {end_time_str}\n')
                            thumbnails_vtt_file.write(f'{storyboard_image_url}#xywh={w_index},{h_index},{width},{height}\n\n')
                    storyboard_image.save(storyboard_path)

        chown_directory(video_dir)
        video.video_dir = video_dir
        video.thumbnails_vtt.name = f'{thumbnails_vtt_path.relative_to(MEDIA_ROOT_DIR)}'
        video.save()


@job('default', timeout=(60 * 20))
def task_audio_stream_generator(object_pk):
    audio = ContentBlockAudio.objects.get(pk=object_pk)

    if audio.has_original():
        original_path = Path(audio.original.path)

        audio_dir = MEDIA_ROOT_DIR / 'audio' / f'audio_{audio.pk}'
        cleanup_directory(audio_dir)
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_stream_path = audio_dir / 'stream.ogg'

        # use ffmpeg to generate audio file (uses silenceremove filter to trims opening and closing silence)
        subprocess.run(
f'''{DH_MAPPING_FFMPEG} -i {original_path.absolute()}
-af "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.1:detection=peak,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.1:detection=peak,areverse"
-c:a libopus -b:a 256k
{audio_stream_path.absolute()}'''.replace('\n', ' '),
            shell=True, check=True, capture_output=True, timeout=(60 * 15)
        )

        chown_directory(audio_dir)
        audio.audio_dir = audio_dir
        audio.audio.name = f'{audio_stream_path.relative_to(MEDIA_ROOT_DIR)}'
        audio.save()