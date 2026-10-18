# EventCreate

EventCreate is a Django event registration platform for discovering local events, saving a seat, and managing an event program from a compact organizer dashboard. Its visual direction uses a dark navy foundation, restrained orange-to-amber accents, and translucent panels inspired by the supplied interface references.

## Features

- Responsive public event listing with title search and category, date-range, and location filters.
- Separate `accounts`, `events`, `registrations`, and `core` apps for account, event, registration, and health-check responsibilities.
- Event detail pages with date, venue, optional map link, attendee count, remaining seats, full and cancelled states.
- User signup, login, profile, one registration per user/event, and cancellation that releases the seat.
- One account-created notification email on signup. There are no email verification links or registration confirmation emails.
- Staff dashboard with event and registration totals, near-capacity view, event CRUD, cancellation notices, and attendee CSV export.
- JSON API for event list, detail, and authenticated registration, with anonymous and signed-in request throttles.
- PostgreSQL configuration with SQLite as the local default.
- Demo data command and tests for the main registration and API flows.

## Tech stack

- Python 3.10+
- Django 5.2.6
- Django REST Framework 3.16.1
- PostgreSQL or SQLite
- Tailwind CSS and DaisyUI via CDN; no Node.js build step
- Small vanilla JavaScript and custom responsive CSS

## Installation

Create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DJANGO_SECRET_KEY` in `.env` to a unique, random value. In local development (`DJANGO_DEBUG=True` in `.env`), the project file takes precedence over any stale `DJANGO_SECRET_KEY` inherited from a terminal. You do not need to export or regenerate the key when opening another terminal. In production (`DJANGO_DEBUG=False`), environment-provided settings take precedence. Keep `.env` on your computer and out of Git. The provided email backend writes outgoing messages to the console during local development.
Never commit `.env`. `DJANGO_DEBUG` defaults to `False`; enable it only for local development so `runserver` serves project static files. For deployment, keep debug off, set `DJANGO_ALLOWED_HOSTS`, use HTTPS, enable `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE`, and set `SECURE_HSTS_SECONDS` after confirming HTTPS works. Run `python manage.py check --deploy` against the production environment before release.

## Database setup

SQLite is selected by default and stores data in `db.sqlite3`:

```powershell
python manage.py migrate
```

To use PostgreSQL, create a database and configure `DB_ENGINE=postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` in `.env`, then run migrations:

```powershell
python manage.py migrate
```

Create an organizer account with `python manage.py createsuperuser`. Staff accounts can manage events from the organizer dashboard and Django admin.

## Sample data and run

```powershell
python manage.py load_sample_data
python manage.py runserver 127.0.0.1:8001
```

Open http://127.0.0.1:8001/. Port `8000` may be used by another local project. Uploaded event images are stored under `media/` in development. In production, run `python manage.py collectstatic` and serve static and uploaded media using a production web server or object storage.

## API endpoints

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| GET | `/api/events/` | Public | List events; optional `q`, `category`, `location`, `from`, and `to` query parameters |
| GET | `/api/events/<id>/` | Public | Retrieve event detail and seat count |
| POST | `/api/events/<id>/register/` | Authenticated | Register the signed-in user for an event |
| GET | `/health/` | Public | Lightweight application health check |

The API uses session authentication when accessed within the site. DRF throttles anonymous requests to 60/hour and authenticated users to 300/hour. Browser forms use Django CSRF protection.

## Screenshots

Add screenshots here for:

- [ ] Event discovery page
- [ ] Event detail and registration
- [ ] Profile with upcoming events
- [ ] Organizer dashboard

## Running tests

```powershell
python manage.py test
```
