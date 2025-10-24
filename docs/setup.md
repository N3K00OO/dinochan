# Setup & operations

## Prerequisites

- Python 3.11+
- Virtual environment (recommended)
- SQLite (default) or a PostgreSQL-compatible database

## Installation steps

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and update the secret key plus database settings.
4. Run migrations via `python manage.py migrate`.
5. Create a superuser: `python manage.py createsuperuser`.
6. Start the dev server: `python manage.py runserver`.

## Tailwind usage

Tailwind CSS loads from the CDN with a restricted configuration defined in `templates/base.html`. If you need to customise the palette or fonts, adjust the `tailwind.config` object and reuse the semantic utility classes provided.

## Running tests

Use Django's test runner:

```bash
python manage.py test
```

## Data seeding

You can populate sample venues through the Django admin UI or by creating fixtures. The models are structured to support factories when integrating with tools such as `factory_boy`.
