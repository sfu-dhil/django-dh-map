# Node deps
FROM node:25.5 AS example-vite
WORKDIR /app

RUN npm upgrade -g npm \
    && npm upgrade -g yarn \
    && rm -rf /var/lib/apt/lists/*

# build js deps
COPY example/example_vite/package.json example/example_vite/yarn.lock /app/
RUN yarn

# run vite build
COPY example/example_vite /app
RUN yarn build

FROM example-vite AS example-vite-prod
RUN yarn --production \
    && yarn cache clean

# Django app
FROM python:3.14-alpine AS example
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

# add prod assets
COPY --from=example-vite-prod /app/dist /static-vite/dist

# collect static assets for production
RUN python manage.py collectstatic --noinput

# run migrations and start server
CMD ["docker/docker-entrypoint.sh"]