import shutil
from pathlib import Path
from typing import List
from django.apps import AppConfig
from django.core.checks import Error, Warning as CheckWarning, register, Tags

class DjangoDhMapConfig(AppConfig):
    name = 'django_dh_map'
    verbose_name = 'Digital Humanities Maps'

    def ready(self):
        import django_dh_map.signals
        register(check_ffmpeg_availability, Tags.compatibility)
        register(check_gdal_availability, Tags.compatibility)


def check_ffmpeg_availability(app_configs, **kwargs) -> List[Error]:
    from .settings import DH_MAPPING_FFMPEG, DH_MAPPING_FFPROBE
    errors = []
    if not shutil.which(DH_MAPPING_FFMPEG):
        errors += [Error(
            "FFmpeg not found",
            hint=(f'FFmpeg binary not found at "{DH_MAPPING_FFMPEG}". Install FFmpeg or set DH_MAPPING_FFMPEG setting to correct path.')
        )]
    if not shutil.which(DH_MAPPING_FFPROBE):
        errors += [Error(
            "FFprobe not found",
            hint=(f'FFprobe binary not found at "{DH_MAPPING_FFPROBE}". Install FFmpeg or set DH_MAPPING_FFPROBE setting to correct path.')
        )]
    return errors

def check_gdal_availability(app_configs, **kwargs) -> List[Error]:
    from .settings import GDAL_LIBRARY_PATH, GEOS_LIBRARY_PATH, DH_MAPPING_GDAL2TILES
    errors = []
    if not shutil.which(GDAL_LIBRARY_PATH):
        errors += [Error(
            "gdal not found",
            hint=(f'gdal binary not found at "{GDAL_LIBRARY_PATH}". Install gdal or set GDAL_LIBRARY_PATH setting to correct path.')
        )]
    if not shutil.which(GEOS_LIBRARY_PATH):
        errors += [Error(
            "geos not found",
            hint=(f'geos binary not found at "{GEOS_LIBRARY_PATH}". Install geos or set GEOS_LIBRARY_PATH setting to correct path.')
        )]
    if not shutil.which(DH_MAPPING_GDAL2TILES):
        errors += [Error(
            "gdal2tiles not found",
            hint=(f'gdal2tiles binary not found at "{DH_MAPPING_GDAL2TILES}". Install gdal-tools or set DH_MAPPING_GDAL2TILES setting to correct path.')
        )]
    return errors