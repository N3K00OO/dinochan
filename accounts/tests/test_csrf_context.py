"""Tests ensuring CSRF token exposure for templates."""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CsrfTokenContextTests(TestCase):
    """Ensure views render with CSRF information available for JavaScript."""

    def test_home_view_sets_csrf_cookie_and_meta_tag(self) -> None:
        user_model = get_user_model()
        user_model.objects.create_user("csrf-user", password="testpass123")
        self.client.login(username="csrf-user", password="testpass123")

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        # The CSRF cookie should always be set so our JavaScript can send it back.
        self.assertIn(settings.CSRF_COOKIE_NAME, response.cookies)
        csrf_cookie = response.cookies[settings.CSRF_COOKIE_NAME].value

        # The rendered template should embed the token in the meta tag for easy lookup.
        html = response.content.decode()
        meta_tag = '<meta name="csrf-token" content="'
        start = html.find(meta_tag)
        self.assertNotEqual(start, -1)
        start += len(meta_tag)
        end = html.find('"', start)
        self.assertNotEqual(end, -1)
        meta_token = html[start:end]
        self.assertEqual(meta_token, csrf_cookie)
