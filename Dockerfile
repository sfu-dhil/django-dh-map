FROM python:3.14-alpine
EXPOSE 80
WORKDIR /app

# add system deps
RUN apk update \
    && apk upgrade \
    && apk --no-cache add git libmagic curl ffmpeg \
        gdal geos gdal-tools \
        gdal-driver-webp gdal-driver-png gdal-driver-jpeg gdal-driver-heif \
    && pip install --no-cache-dir --upgrade pip \
    && rm -rf /var/cache/apk/*

# install python deps
COPY example/requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir

# add project files
COPY example /app
COPY django_dh_map /app/django_dh_map

# collect static assets for production
RUN python manage.py collectstatic --noinput

# run migrations and start server
CMD ["docker/docker-entrypoint.sh"]