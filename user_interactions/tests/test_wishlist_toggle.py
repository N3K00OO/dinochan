"""Tests for wishlist toggle API behaviour."""

from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from field_management.models import Category, Venue
from user_interactions.models import Wishlist


class WishlistToggleAPITests(TestCase):
    """Ensure the wishlist toggle endpoint behaves as expected."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="wishlist-user",
            email="wishlist@example.com",
            password="strong-pass-123",
        )
        self.category = Category.objects.create(name="Futsal Court")
        self.venue = Venue.objects.create(
            category=self.category,
            name="Downtown Arena",
            description="Indoor futsal court with premium flooring.",
            location="Downtown",
            city="Jakarta",
            address="123 Central Street",
            price_per_hour=Decimal("150000.00"),
            capacity=10,
            facilities="Locker room, Shower",
            image_url="https://example.com/image.jpg",
        )

    def test_toggle_creates_and_removes_wishlist(self) -> None:
        self.client.force_login(self.user)

        toggle_url = reverse("wishlist-toggle-api", args=[self.venue.pk])

        first_response = self.client.post(
            toggle_url,
            data="{\"next\": \"/catalog/\"}",
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(first_response.status_code, 200)
        first_payload = first_response.json()
        self.assertTrue(first_payload["wishlisted"])
        self.assertEqual(first_payload["wishlist_count"], 1)
        self.assertIsInstance(first_payload["wishlist_item_html"], str)
        self.assertIn(str(self.venue.pk), first_payload["wishlist_item_html"])
        self.assertEqual(first_payload["venue"]["id"], str(self.venue.pk))
        self.assertEqual(first_payload["venue"]["name"], self.venue.name)
        self.assertEqual(first_payload["venue"]["toggle_url"], toggle_url)
        self.assertIn('name="next" value="/catalog/"', first_payload["wishlist_item_html"])
        self.assertTrue(Wishlist.objects.filter(user=self.user, venue=self.venue).exists())

        second_response = self.client.post(
            toggle_url,
            data="{}",
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(second_response.status_code, 200)
        second_payload = second_response.json()
        self.assertFalse(second_payload["wishlisted"])
        self.assertEqual(second_payload["wishlist_count"], 0)
        self.assertIsNone(second_payload["wishlist_item_html"])
        self.assertEqual(second_payload["venue"]["id"], str(self.venue.pk))
        self.assertEqual(second_payload["venue"]["toggle_url"], toggle_url)
        self.assertFalse(Wishlist.objects.filter(user=self.user, venue=self.venue).exists())

    def test_toggle_requires_authentication(self) -> None:
        toggle_url = reverse("wishlist-toggle-api", args=[self.venue.pk])
        response = self.client.post(toggle_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("auth:login"), response.url)

    def test_non_ajax_toggle_redirects_with_next(self) -> None:
        self.client.force_login(self.user)
        next_url = reverse("catalog")
        toggle_url = reverse("wishlist-toggle", args=[self.venue.pk])

        response = self.client.post(toggle_url, data={"next": next_url})

        self.assertRedirects(response, next_url, fetch_redirect_response=False)
        self.assertTrue(Wishlist.objects.filter(user=self.user, venue=self.venue).exists())
