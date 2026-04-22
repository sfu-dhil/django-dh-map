# inspired by https://github.com/jhoriascos/django-bsicon/blob/main/scripts/update_icons.py
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BOOTSTRAP_ICONS_JSON_FILE = SCRIPT_DIR / '../vite/node_modules/bootstrap-icons/font/bootstrap-icons.json'

def get_key(name):
    return f'BI_{name.replace('-', '_').upper()}'

def get_value(name):
    return f'bi bi-{name}'

def get_label(name):
    return f'<i class="{get_value(name)}></i> {name.replace('-', ' ')}'

with open(BOOTSTRAP_ICONS_JSON_FILE.resolve(), 'r') as bootstrap_icon_json_file:
    data = json.load(bootstrap_icon_json_file)

    print(f'Icons:')
    for name in data.keys():
        print((' ' * 4) + f"{get_key(name)} = '{get_value(name)}', '{get_label(name)}' ")
