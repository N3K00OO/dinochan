# RagaSpace

RagaSpace is a secure, modern venue booking platform built with Django, Tailwind CSS, and progressive enhancement techniques. The experience combines a cohesive glassmorphism-inspired UI, cinematic micro-interactions, and robust booking workflows that cover discovery, wishlist management, checkout, and review sharing.

## Features

- 🔐 **Secure authentication** — Login, register, and logout flows backed by Django's authentication system and hardened session settings.
- 🏠 **Landing experience** — Hero search, curated highlights, and quick filters driven by AJAX for instant catalogue updates.
- 📚 **Catalog & filtering** — Rich venue listings with city, category, and price filters powered by `django-filter`.
- 💖 **Wishlist** — Add/remove favourites with asynchronous updates and persistent storage per user.
- 📅 **Booking & payment** — Collect schedule preferences, optional add-ons, and capture payment intents with invoice summaries.
- ⭐ **Reviews** — First-party reviews linked to verified users with edit-safe defaults.

## Getting started

1. **Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Environment variables** — copy `.env.example` (see below) and adjust secrets.
3. **Database & demo data**
   ```bash
   python manage.py migrate
   python manage.py seeddemo  # creates sample venues, demo accounts, and an initial admin
   ```
4. **Run**
   ```bash
   python manage.py runserver
   ```
5. Visit `http://127.0.0.1:8000/` and log in to explore the dashboard.

## Tech stack & practices

- **Backend** — Django 4 with `django-filter` for secure, maintainable filtering.
- **Frontend** — Tailwind CSS via CDN, small vanilla JavaScript for wishlist and catalogue AJAX interactions.
- **Security** — CSRF protection, secure cookie toggles, password validators, and environment-driven secrets.
- **Architecture** — Modular app (`venues`) encapsulating models, forms, filters, views, signals, and templates.
- **Documentation** — Additional guides live under [`docs/`](docs/).

## Testing

```bash
python manage.py test
```

Feel free to explore the dedicated admin workspace at `/workspace/` once logged in as a staff member. It provides CRUD tools for venues and the ability to invite additional administrators.
