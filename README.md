# Research Registry API

This project is a Django REST API for managing research studies, participants, and applications.
It simulates a backend service that could be used in a research environment to register studies,
collect participant applications, and manage approval workflows.

The project is built with Django, Django REST Framework, PostgreSQL, and Docker.

---

## Features

* Custom user model with roles (admin / researcher)
* Study management
* Participant management
* Application workflow
* Approve / reject actions
* Object-level permissions
* Filtering, search, ordering, pagination
* Seed demo data
* Docker setup with PostgreSQL
* Ready for Gunicorn + Nginx deployment

---

## Tech Stack

* Python 3
* Django
* Django REST Framework
* PostgreSQL
* Docker / Docker Compose
* django-filter

---

## Project Structure

backend/
accounts/
studies/
participants/
applications/
core/
research_registry/

docker-compose.yml
start.sh
README.md

---

## Setup

### 1. Clone repository

git clone <repo>
cd research_registry

### 2. Create env file

cp .env.example .env

Edit values if needed.

### 3. Start with docker

./start.sh

or manually

docker compose up --build

### 4. Run migrations

docker compose exec web python manage.py migrate

### 5. Initialize roles

docker compose exec web python manage.py init_roles

### 6. Seed demo data

docker compose exec web python manage.py seed_demo_data

### 7. Create superuser

docker compose exec web python manage.py createsuperuser

---

## API

Base URL

http://localhost:8000/api/

Examples

GET /api/studies/
GET /api/studies/?search=memory
GET /api/studies/?status=active
GET /api/studies/?page=2

POST /api/applications/1/approve/
POST /api/applications/1/reject/

GET /api/me/

Browsable API

http://localhost:8000/api-auth/login/

---

## Permissions

Admin:

* full access

Researcher:

* access only own studies and applications

Anonymous:

* read-only

---

## Development

Run shell

docker compose exec web python manage.py shell

Run tests

docker compose exec web python manage.py test

---

## Future Improvements

* JWT authentication
* Export CSV
* File uploads
* Study tags
* Email notifications
* Logging
* Audit trail
* Production deployment with Gunicorn + Nginx

---

## License

Example project for learning Python and Django.

