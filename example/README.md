## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Initialize the Application

    docker compose up -d --build

Example App will be available at `http://localhost:8080/`
Example Admin will be available at `http://localhost:8080/admin/`

### Install/Switch the admin theme

    # Bootstrap
    docker exec -it django_dh_map_app python manage.py loaddata admin_interface_theme_bootstrap.json

### Create your superuser

    docker exec -it django_dh_map_app python manage.py createsuperuser

Enter `username`, `email`, and `password` as prompted

example:

    docker exec -it django_dh_map_app python manage.py createsuperuser --username="admin" --email="dhil@sfu.ca"

## General Usage

### Starting the Application

    docker compose up -d

### Stopping the Application

    docker compose down

### Rebuilding the Application (after upstream or js/python package changes)

    docker compose up -d --build

### Viewing logs (each container)

    docker logs -f django_dh_map_app
    docker logs -f django_dh_map_worker
    docker logs -f django_dh_map_nginx
    docker logs -f django_dh_map_db
    docker logs -f django_dh_map_mail

### Accessing the Application

    http://localhost:8080/

### Accessing the Database

Command line:

    PGPASSWORD=password docker exec -it django_dh_map_db psql --username=django_dh_map django_dh_map

Through a database management tool:
- Host:`127.0.0.1`
- Port: `15432`
- Username: `django_dh_map`
- Password: `password`

### Accessing Mailhog (catches emails sent by the app)

    http://localhost:8025/

### Database Migrations

Migrate up to latest

    docker exec -it django_dh_map_app python manage.py migrate

Create new migrations

    docker exec -it django_dh_map_app python manage.py makemigrations
