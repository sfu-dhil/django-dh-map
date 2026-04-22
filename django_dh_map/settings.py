
from django.conf import settings
from pathlib import Path
from datetime import date

# media dirs
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', '/media')
MEDIA_URL = getattr(settings, 'MEDIA_URL', '/')
MEDIA_ROOT_DIR = Path(MEDIA_ROOT)
MEDIA_FOLDER_UID = getattr(settings, 'MEDIA_FOLDER_UID', 101)
MEDIA_FOLDER_GID = getattr(settings, 'MEDIA_FOLDER_GID', 101)

# mapping
GDAL_LIBRARY_PATH = getattr(settings, 'GDAL_LIBRARY_PATH', None)
GEOS_LIBRARY_PATH = getattr(settings, 'GEOS_LIBRARY_PATH', None)
DH_MAPPING_GDAL2TILES = getattr(settings, 'DH_MAPPING_GDAL2TILES', 'gdal2tiles')
DH_MAPPING_GDAL2TILES_S_SRS = getattr(settings, 'DH_MAPPING_GDAL2TILES_S_SRS', 0)
DH_MAPPING_OVERHEAD_TILE_SIZE = getattr(settings, 'DH_MAPPING_OVERHEAD_TILE_SIZE', 128)
DH_MAPPING_PANORAMA_TILE_SIZE = getattr(settings, 'DH_MAPPING_PANORAMA_TILE_SIZE', 512)

# Video post-processing
DH_MAPPING_FFMPEG = getattr(settings, 'DH_MAPPING_FFMPEG', 'ffmpeg')
DH_MAPPING_FFPROBE = getattr(settings, 'DH_MAPPING_FFPROBE', 'ffprobe')
DH_MAPPING_VIDEO_SEGMENT_DURATION = getattr(settings, 'DH_MAPPING_VIDEO_SEGMENT_DURATION', 2)
DH_MAPPING_VIDEO_THUMBNAIL_INTERVAL = getattr(settings, 'DH_MAPPING_VIDEO_THUMBNAIL_INTERVAL', 2)
DH_MAPPING_VIDEO_RESOLUTIONS = getattr(settings, 'DH_MAPPING_VIDEO_RESOLUTIONS', [
    {"height": 360, "bitrate": 1200},   # SD/mobile
    {"height": 720, "bitrate": 2500},   # HD
    {"height": 1080, "bitrate": 4500},  # Full HD
    # {"height": 1440, "bitrate": 8000},  # 2K
    # {"height": 2160, "bitrate": 20000}, # 4K
])