This is an package mainly for in-house usage. There are a lot of admin packages used that might not work well in your environment (ex: `django-rq` instead of `celery` for background jobs). Its primary goal is to help springboard new Digital Humanities mapping projects with a decent amount of flexability around often requested features.

If you cannot directly use this package, consider forking to customizing for your own usage/environment or just use it for inspiration.

## Requirements

- `gdal`, `gdal-tools` for postgis and overhead tile generation
- `ffmpeg` for video resolution and thumbnail generation
- `libmagic` for image processing
- `redis` for background job support
- Assumes `postgres` database with gis (`postgis`)


## Build assets

    # install node_modules
    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn

    # build assets and watch for changes
    docker run --rm -it -v $PWD:/app/ -w /app/vite node:25.5 yarn watch