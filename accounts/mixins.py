"""Reusable mixins shared across the project."""
from __future__ import annotations

from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin ensuring the current user is an administrator."""

    def test_func(self):
        return bool(self.request.user and self.request.user.is_staff)

    def handle_no_permission(self):  # pragma: no cover - relies on Django's redirect
        from django.contrib import messages
        from django.shortcuts import redirect

        messages.error(self.request, "You do not have access to the admin workspace.")
        return redirect("home")


class EnsureCsrfCookieMixin:
    """Guarantee the CSRF cookie is present for JavaScript powered pages."""

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):  # type: ignore[override]
        return super().dispatch(request, *args, **kwargs)
