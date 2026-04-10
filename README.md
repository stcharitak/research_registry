# Research Registry API

A Django REST API for managing research studies, participant records, and application review workflows.

## What This Project Does

- Manages studies created by researchers
- Stores participant profiles
- Handles study applications and review decisions
- Uses role-based access control (`admin`, `researcher`)
- Supports filtering, search, ordering, and pagination
- Provides asynchronous data export functionality (CSV)

## Architecture Highlights

This project follows a layered architecture to keep business logic clean and testable:

- **Views (API layer)** – handle HTTP requests/responses  
- **Permissions** – enforce access control at the API level  
- **Service Layer** – contains core business logic (e.g. approve/reject workflows)  
- **Models** – database representation  

Key idea:

> Business logic is not implemented in views or serializers, but in dedicated service classes.

This makes the system easier to:
- test  
- extend  
- reuse  

## Tech Stack

- Python 3
- Django 6
- Django REST Framework
- PostgreSQL 17
- Celery (background workers)
- RabbitMQ (message broker)
- Docker / Docker Compose
- Ruff (linting & formatting)
- Coverage.py (test coverage)
- `django-filter`

## Project Structure

```text
research_registry/
├── backend/
│   ├── research_registry/   # Django project settings + root URLs
│   ├── accounts/            # Users, roles, auth
│   ├── studies/             # Study resources
│   ├── participants/        # Participant resources
│   ├── applications/        # Application resources + review logic
│   │   └── services/
│   │       └── application_export_service.py
│   ├── exports/             # Export system (jobs, tasks, API)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── tasks.py
│   │   └── constants.py
│   ├── Dockerfile
│   └── requirements.txt
```

## Export System (Async CSV Export)

This project includes a production-style export system using background workers.

### Key Features
Export large datasets as CSV
Runs asynchronously via Celery workers
Uses RabbitMQ as message broker
Tracks export status (pending, processing, completed, failed)
Stores generated files using Django FileField
Enforces user-level permissions on exported data

### How It Works
1. User requests an export via API
2. An ExportJob is created in the database
3. A Celery worker processes the job asynchronously
4. Data is written to a CSV file
5. File is stored under /media/exports/
6. User can check status and download when ready

## Quick Start (Recommended)

1. Clone and enter the project:

```bash
git clone <your-repo-url>
cd research_registry
```

2. Create environment file:

```bash
cp .env.example .env
```
Then configure the .env file with your environment-specific values (e.g. database credentials, passwords, and secret keys).

3. Start everything (build, migrate, init roles, seed data):

```bash
make up
```

API base URL after startup:

```text
http://localhost:8000/api/
```
## Useful Development Commands

Using Makefile:

```bash
make up        # full setup
make test       # run tests + coverage
make test-fast  # run tests without coverage
make lint       # lint code (ruff)
make format     # format code
make fix        # auto-fix lint issues
```

Open Django shell:

```bash
docker compose exec web python manage.py shell
```

## Manual Setup Commands

```bash
docker compose up -d --build
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py init_roles
docker compose exec web python manage.py seed_demo_data
```

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Create a researcher user (interactive prompt):

```bash
docker compose exec web python manage.py create_researcher
```

## Authentication Flow (JWT)

Get access and refresh tokens:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<username>","password":"<password>"}'
```

Refresh access token:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

Call authenticated endpoint:

```bash
curl http://localhost:8000/api/me/ \
  -H "Authorization: Bearer <access_token>"
```

## API Endpoints (Current)

All routes below reflect the current URL configuration in this repository.

### Auth and Account

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/token/` | Obtain JWT access/refresh token pair |
| `POST` | `/api/token/refresh/` | Refresh JWT access token |
| `GET` | `/api/me/` | Current authenticated user profile |

### Studies

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/studies/` | List studies |
| `POST` | `/api/studies/` | Create study |
| `GET` | `/api/studies/{id}/` | Retrieve study |
| `PUT` | `/api/studies/{id}/` | Replace study |
| `PATCH` | `/api/studies/{id}/` | Partially update study |
| `DELETE` | `/api/studies/{id}/` | Delete study |

Query support on list endpoint:

- Filters: `status`, `created_by`
- Search: `search` (title, description)
- Ordering: `ordering` (`created_at`, `title`)

### Participants

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/participants/` | List participants |
| `POST` | `/api/participants/` | Create participant |
| `GET` | `/api/participants/{id}/` | Retrieve participant |
| `PUT` | `/api/participants/{id}/` | Replace participant |
| `PATCH` | `/api/participants/{id}/` | Partially update participant |
| `DELETE` | `/api/participants/{id}/` | Delete participant |

### Applications

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/applications/` | List applications |
| `POST` | `/api/applications/` | Create application |
| `GET` | `/api/applications/{id}/` | Retrieve application |
| `PUT` | `/api/applications/{id}/` | Replace application |
| `PATCH` | `/api/applications/{id}/` | Partially update application |
| `DELETE` | `/api/applications/{id}/` | Delete application |
| `POST` | `/api/applications/{id}/approve/` | Approve application |
| `POST` | `/api/applications/{id}/reject/` | Reject application |


### Exports

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/exports/` | Create an asynchronous export job for a specific resource type (e.g. applications) with optional filtering. |
| `GET` | `/api/exports/` | List all export jobs created by the authenticated user, ordered by most recent. |
| `GET` | `/api/exports/{id}/` | Retrieve the status and details of a specific export job, including the download URL when available. |

Query support on list endpoint:

- Filters: `status`, `study`, `participant`, `reviewed_by`
- Search: `search` (`status`, `study__id`, `participant__id`, `reviewed_by__username`)
- Ordering: `ordering` (`id`, `status`, `reviewed_by`)

### Extra Routes

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/` | Django admin |
| `GET` | `/api-auth/login/` | DRF browsable API login |
| `GET` | `/api-auth/logout/` | DRF browsable API logout |

## Pagination

Default page size is `5` items per page (`PageNumberPagination`).

Example:

```text
GET /api/studies/?page=2
```

## Permissions (High Level)

- `admin`: full access
- `researcher`: access based on ownership/business rules
- anonymous users: read-only where allowed

## Future Improvements

- CSV export
- Expanded audit tooling
- Production hardening (Gunicorn/Nginx, security settings)

## License

Educational/demo project for learning Django + DRF architecture.
