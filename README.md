This is an package mainly for in-house usage. There are a lot of admin packages used that might not work well in your environment (ex: `django-rq` instead of `celery` for background jobs). Its primary goal is to help springboard new Digital Humanities mapping projects with a decent amount of flexability.

If you cannot directly use this package, consider forking and customizing for your own usage/environment or just use it for inspiration.

## Requirements

- `gdal`, `gdal-tools` for postgis and overhead tile generation
- `ffmpeg` for video resolution and thumbnail generation
- `libmagic` for image processing
- `redis` for background job support
- Assumes `postgres` database with gis (`postgis`)

## Install

Add all the deps (including `django_dh_map`) to your `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...,
    'django_dh_map',
    'admin_interface',
    'colorfield',
    'nested_admin',
    'django_jsonform',
    'adminsortable2',
    'solo',
    'tinymce',
    'admin_async_upload',
    'imagekit',
    'django_rq',
    'django.contrib.gis',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'polymorphic',
    'rest_framework',
    'rest_framework_gis',
    ...,
]
```

Add the urls to your project


```python
urlpatterns = [
    ...,
    # django-async-upload endpoints
    path('admin_async_upload/', include('admin_async_upload.urls')),
    # tinymce endpoints
    path('tinymce/', include('tinymce.urls')),
    # django_rq admin endpoints
    path('django-rq/', include('django_rq.urls')),
    # django_dh_map endpoints
    path('', include("django_dh_map.urls")),
    ...,
]
```

Run `python manage.py migrate`

Include the package javascript and css into your `base.html` file's head section

```html
{% load static %}
...
<head>
    ...
    <link rel="stylesheet" href="{% static 'django_dh_map/dist/django_dh_map.css' %}">
    <script src="{% static 'django_dh_map/dist/django_dh_map.js' %}" defer></script>
    ...
</head>
```

## Example Project

See [example/README.md](https://github.com/sfu-dhil/django-dh-map/blob/main/example/README.md) for instructions for running the example app (using Docker). Run the `docker compose` commands from the root directory.

## Development

### Build assets

    # install node_modules
    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn

    # build assets
    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn build

    # build assets and watch for changes
    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn watch
    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn watch_dist

<!--
### Manually update Bootstrap/Fontawesome icon selector

    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn
    docker run --rm -it -v $PWD:/app/ -w /app python:3.14-alpine python scripts/get_bootstrap_icons_choices.py

./:/app/django_dh_map

    # build assets and watch for changes
    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn watch -->