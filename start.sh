#!/bin/bash

set -e

echo "=== Starting project ==="

docker compose up -d --build

echo "Waiting for Django..."

until docker compose exec web python manage.py check > /dev/null 2>&1
do
  sleep 2
done

echo "Make migrations"
docker compose exec web python manage.py makemigrations

echo "Migrate"
docker compose exec web python manage.py migrate

echo "Init roles"
docker compose exec web python manage.py init_roles

echo "Create superuser (if not exists)"

docker compose exec web \
  sh -c "
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print('Superuser created')
else:
    print('Superuser already exists')
EOF
"

echo "Seed demo data"
docker compose exec web python manage.py seed_demo_data

echo "=== Ready ==="