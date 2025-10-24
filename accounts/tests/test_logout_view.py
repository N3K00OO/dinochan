"""Tests for the authentication logout view."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthLogoutViewTests(TestCase):
    """Ensure the custom logout view behaves as expected."""

    def setUp(self) -> None:
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="logout-user",
            email="logout@example.com",
            password="secret123",
        )

    def test_get_logout_redirects_and_logs_user_out(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(reverse("auth:logout"), follow=True)

        self.assertRedirects(response, reverse("auth:login"))
        self.assertFalse(response.context["user"].is_authenticated)
        messages = list(response.context["messages"])
        self.assertTrue(any("logged out" in str(message) for message in messages))

    def test_post_logout_redirects_and_logs_user_out(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(reverse("auth:logout"), follow=True)

        self.assertRedirects(response, reverse("auth:login"))
        self.assertFalse(response.context["user"].is_authenticated)

    def test_logout_requires_authentication(self) -> None:
        response = self.client.get(reverse("auth:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("auth:login"), response.headers["Location"])
