# Common Ground — Backend

Backend API for **Common Ground**, a real-time discussion platform built with Django and Django REST Framework.

The application allows users to create comments, reply to discussions, upload attachments, and receive real-time updates. It supports both guest participation and JWT-based authentication.

## Tech Stack

- Python 3.12 (Docker)
- Django 6
- Django REST Framework
- PostgreSQL 15
- Django Channels and Daphne
- Redis
- Celery
- Simple JWT
- Django Simple Captcha
- Docker and Docker Compose

## Features

### Comments and Discussions

- Create comments as a guest or registered user
- Reply to existing comments
- Display nested comment threads
- Sort discussions by creation date, username, or email
- Ascending and descending sorting
- Pagination with 25 root comments per page

### Authentication

- User registration
- Login with JWT authentication
- Access and refresh tokens
- Token refresh and logout
- Protected user profile endpoint

### Security and Validation

- CAPTCHA verification when submitting comments
- Server-side input validation
- HTML sanitization
- Support for a limited set of HTML tags: `strong`, `i`, `code`, and `a`
- Protection against unsafe HTML and JavaScript injection
- Attachment type and size validation

### File Attachments

Supported formats:

- JPG
- PNG
- GIF
- TXT

Images are limited to 320 × 240 pixels. TXT files are limited to 100 KB and must contain valid UTF-8 text.

### Real-Time Updates

WebSocket connections are implemented using Django Channels and Redis.

When a new comment is created, the backend broadcasts an event so connected clients can update their discussions.

### Background Processing and Caching

- Redis caching for comment listings
- Cache invalidation after changes
- Celery for asynchronous attachment processing
- Redis as the Celery message broker

## Project Structure

```text
spa-test/
├── attachments/
├── comments/
├── users/
├── spa/
├── media/
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

## Running with Docker

Docker Compose runs PostgreSQL, Redis, Django, Celery, and the React frontend.

The expected directory structure is:

```text
project/
├── frontend/
└── spa-test/
```

The frontend directory must be located next to `spa-test` because Docker Compose uses `../frontend` as its build context.

**1. Start the application**

From the backend directory:

```bash
docker compose up -d --build
```

**2. Apply database migrations**

```bash
docker compose exec backend python manage.py migrate
```

**3. Check running containers**

```bash
docker compose ps
```

**4. Open the application**

Frontend:

http://localhost:8080

Backend API:

http://localhost:8000

**5. Stop the application**

```bash
docker compose down
```

Do not use `docker compose down -v` unless you intentionally want to delete the database volume.

## Running Locally Without Docker

Python and a running PostgreSQL and Redis instance are required.

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Apply migrations:

```bash
python3 manage.py migrate
```

Start Django:

```bash
python3 manage.py runserver --noreload
```

Start Celery in another terminal:

```bash
celery -A spa worker --loglevel=info --pool=solo
```

The backend uses environment variables to configure PostgreSQL and Redis. Local defaults are available in the Django settings.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/comments/` | List comments |
| GET | `/comments/{id}/` | Get a comment |
| POST | `/comments/create/` | Create a comment |
| GET | `/comments/{id}/replies/` | Get replies |
| POST | `/comments/{id}/replies/` | Create a reply |
| POST | `/comments/{id}/attachments/` | Upload an attachment |
| GET | `/api/captcha/` | Generate CAPTCHA |
| POST | `/api/auth/register/` | Register user |
| POST | `/api/auth/login/` | Log in |
| POST | `/api/auth/refresh/` | Refresh JWT |
| POST | `/api/auth/logout/` | Log out |

### Pagination and Sorting

Example:

```http
GET /comments/?page=1&sort=created_at&order=desc
```

Supported sorting fields:

- `created_at`
- `user_name`
- `email`

Supported order values: `asc`, `desc`.

### WebSocket

```text
ws://localhost:8000/ws/comments/
```

Example event:

```json
{
  "event": "comment.created",
  "comment": {
    "id": 1,
    "parent": null
  }
}
```

The example shows the main event fields; the actual payload may contain additional comment data.

## Testing

The project includes automated Django tests covering:

- Comment creation
- CAPTCHA validation
- HTML validation and sanitization
- Nested replies
- Pagination
- Sorting
- Registration
- Login
- Authentication protection
- File validation

Run tests locally:

```bash
python3 manage.py test comments users attachments
```

At the time of preparation, **11 automated tests passed successfully**.

## Configuration

The application uses environment-based configuration for database and Redis connections.

Important variables include:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
REDIS_URL
DEBUG
ALLOWED_HOSTS
```

The included Docker Compose setup is intended for local development and testing. Before public deployment, production secrets and security settings must be configured separately.

## Notes

This backend was developed as part of the dZENcode technical assessment.

It demonstrates REST API development, authentication, relational database design, background tasks, caching, real-time communication, file handling, automated testing, and Docker-based application setup.