# inspired by https://github.com/jhoriascos/django-bsicon/blob/main/scripts/update_icons.py
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
FONTAWESOME_ICONS_JSON_FILE = SCRIPT_DIR / '../vite/node_modules/@fortawesome/fontawesome-free/metadata/icon-families.json'

def get_key(name, style):
    return f'FA_{name.replace('-', '_').upper()}_{style.replace('-', '_').upper()}'

def get_value(name, style):
    return f'fa-{style} fa-{name}'

def get_label(name, style, label, with_style=False):
    return f'<i class="{get_value(name, style)}></i> {label}{f' ({style.capitalize()})' if with_style else ''}'

with open(FONTAWESOME_ICONS_JSON_FILE.resolve(), 'r') as fontawesome_icon_json_file:
    data = json.load(fontawesome_icon_json_file)

    print(f'Icons:')
    for name, metadata in data.items():
        # only get classic icons (also skip brands)
        free_family_styles = [
            free_family_style for free_family_style in metadata.get('familyStylesByLicense', {}).get('free', {}) \
            if free_family_style.get('family') == 'classic' and free_family_style.get('style') != 'brands'
        ]
        label_with_style = len(free_family_styles) > 1
        for free_family_style in free_family_styles:
            style = free_family_style.get('style')
            label = metadata.get('label')
            if style and label:
                print((' ' * 4) + f"{get_key(name, style)} = '{get_value(name, style)}', '{get_label(name, style, label, label_with_style)}' ")
