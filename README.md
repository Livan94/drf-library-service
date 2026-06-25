# DRF Library Service

DRF Library Service is a backend application for managing books, users, and borrowings in a library system. It provides authenticated API endpoints, borrowing workflow logic, Docker-based local setup, and interactive API documentation via Swagger and Redoc.

## Features

- Books API for creating, viewing, updating, and deleting books.
- Borrowings API for managing book borrowing operations.
- User registration and authentication with JWT tokens.
- Login using email.
- User profile endpoint for authenticated users.
- PostgreSQL-based data storage.
- Dockerized local development setup.
- Interactive API documentation with Swagger UI and Redoc.

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- drf-spectacular for API schema and documentation.

## Project Apps

- `books` — book model, serializers, views, and related API endpoints.
- `users` — authentication, registration, JWT endpoints, and profile management.
- `borrowings` — borrowing logic and borrowing-related endpoints.

## Implemented Tasks

- Created books API.
- Implemented borrowings functionality.
- Added user registration and authentication.
- Configured JWT authentication.
- Added API documentation with Swagger and Redoc.
- Added pagination and project settings improvements.
- Dockerized the project with PostgreSQL support.
- Added database readiness check with `wait_for_db`.

## Quick Start with Docker

### 1. Clone the repository

```bash
git clone https://github.com/Livan94/drf-library-service.git
cd drf-library-service
```

### 2. Configure environment variables

Create a `.env` file from the sample:

```bash
cp .env.sample .env
```
Make sure the file contains the required variables, including:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

### 3. Build and start containers

```bash
docker compose up --build
```

The application will:
- wait until PostgreSQL is available,
- apply migrations automatically,
- start the Django development server.

### 4. Load test data

If you want to populate the database with fixture data, run:

```bash
docker compose exec web python manage.py loaddata test_data.json
```

### 5. Create superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## API Endpoints

Main API routes:

- `/api/books/`
- `/api/borrowings/`
- `/api/users/`
- `/api/users/me/`
- `/api/users/token/`
- `/api/users/token/refresh/`

## API Documentation

After starting the project, API documentation is available at:

- Swagger UI: [`http://127.0.0.1:8000/api/doc/swagger/`](http://127.0.0.1:8000/api/doc/swagger/)
- Redoc: [`http://127.0.0.1:8000/api/doc/redoc/`](http://127.0.0.1:8000/api/doc/redoc/)
- OpenAPI schema: [`http://127.0.0.1:8000/api/schema/`](http://127.0.0.1:8000/api/schema/)



## Useful Commands

Run migrations manually:

```bash
docker compose exec web python manage.py migrate
```

Create new migrations:

```bash
docker compose exec web python manage.py makemigrations
```

Run tests:

```bash
docker compose exec web python manage.py test
```