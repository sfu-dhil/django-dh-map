import os
import numpy as np
from pathlib import Path

from .settings import MEDIA_FOLDER_UID, MEDIA_FOLDER_GID

def cleanup_directory(dir, recursive=True):
    if dir and isinstance(dir, Path) and dir.exists() and dir.is_dir():
        if recursive:
            children = list(dir.glob('**/*'))
            for file in [child for child in children if child.is_file()]:
                file.unlink(missing_ok=True)
            # ordered directory leafs first
            for sub_dir in sorted([child for child in children if child.is_dir()], key=lambda sd: len(sd.parts), reverse=True):
                sub_dir.rmdir()
        dir.rmdir()

def chown_directory(dir, recursive=True):
    if dir and isinstance(dir, Path) and dir.exists() and dir.is_dir():
        if recursive:
            for child in list(dir.glob('**/*')):
                os.chown(child.absolute(), MEDIA_FOLDER_UID, MEDIA_FOLDER_GID)
        os.chown(dir.absolute(), MEDIA_FOLDER_UID, MEDIA_FOLDER_GID)

def get_success_failure_status_tick(success):
    return '<strong><span style="color: green">✓<span></strong>' if success else '<strong><span style="color: red">x<span></strong>'