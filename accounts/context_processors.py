"""Context processors for authentication module."""
from __future__ import annotations

from django.conf import settings
from django.middleware.csrf import get_token


def csrf_token_context(request):
    """Expose the CSRF cookie value so templates can embed it for JavaScript."""

    token = request.COOKIES.get(settings.CSRF_COOKIE_NAME)
    if not token:
        token = request.META.get("CSRF_COOKIE") or get_token(request)
    return {
        "csrf_cookie_value": token,
    }
