"""Tests for admin venue management actions."""
from __future__ import annotations

from datetime import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django.utils.text import slugify

from field_management.models import Category, Venue


class AdminVenueManagementTests(TestCase):
    """Ensure admin-only venue CRUD operations behave correctly."""

    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username="admin",
            password="Admin123!",
            is_staff=True,
            is_superuser=True,
        )
        self.user = user_model.objects.create_user(username="user", password="User123!")
        self.category = Category.objects.create(name="Sports", slug="sports")

    def _valid_payload(self, name: str = "Sky Arena", slug: str | None = None) -> dict[str, str]:
        return {
            "category": str(self.category.pk),
            "name": name,
            "slug": slug or slugify(name),
            "description": "Spacious indoor arena.",
            "location": "Central City",
            "city": "Metropolis",
            "address": "123 Main Street",
            "price_per_hour": "150000.00",
            "capacity": "250",
            "facilities": "wifi, parking",
            "image_url": "https://example.com/arena.jpg",
            "available_start_time": "08:00",
            "available_end_time": "23:00",
        }

    def test_admin_can_create_venue_from_list_view(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin-venues"), self._valid_payload())

        errors = None
        if hasattr(response, "context") and response.context:
            context = response.context
            if isinstance(context, list):
                context = context[0]
            errors = context.get("venue_form").errors if context.get("venue_form") else None

        self.assertEqual(response.status_code, 302, errors)
        self.assertRedirects(response, reverse("admin-venues"))
        self.assertTrue(Venue.objects.filter(name="Sky Arena").exists())

    def test_non_admin_cannot_create_venue(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("admin-venues"), self._valid_payload(name="Fail Arena"))

        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Venue.objects.filter(name="Fail Arena").exists())

    def test_admin_can_delete_venue(self):
        venue = Venue.objects.create(
            category=self.category,
            name="Sunset Field",
            slug="sunset-field",
            description="Outdoor field",
            location="West District",
            city="Metropolis",
            address="45 Sunset Boulevard",
            price_per_hour="120000.00",
            capacity=150,
            facilities="lighting",
            image_url="https://example.com/field.jpg",
            available_start_time=time(7, 0),
            available_end_time=time(21, 0),
        )

        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin-venue-delete", args=[venue.pk]))

        self.assertRedirects(response, reverse("admin-venues"))
        self.assertFalse(Venue.objects.filter(pk=venue.pk).exists())

    def test_non_admin_cannot_delete_venue(self):
        venue = Venue.objects.create(
            category=self.category,
            name="Aurora Court",
            slug="aurora-court",
            description="Indoor court",
            location="East Park",
            city="Metropolis",
            address="67 Aurora Lane",
            price_per_hour="95000.00",
            capacity=80,
            facilities="scoreboard",
            image_url="https://example.com/court.jpg",
            available_start_time=time(9, 0),
            available_end_time=time(20, 0),
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse("admin-venue-delete", args=[venue.pk]))

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(Venue.objects.filter(pk=venue.pk).exists())

    def test_duplicate_slug_on_create_view_returns_error(self):
        Venue.objects.create(
            category=self.category,
            name="Existing Arena",
            slug="sky-arena",
            description="Existing venue",
            location="Central",
            city="Metropolis",
            address="1 Main Street",
            price_per_hour="150000.00",
            capacity=200,
            facilities="wifi",
            image_url="https://example.com/existing.jpg",
            available_start_time=time(8, 0),
            available_end_time=time(22, 0),
        )

        self.client.force_login(self.admin)
        payload = self._valid_payload(name="Sky Arena")
        payload.update(
            {
                "addons-TOTAL_FORMS": "0",
                "addons-INITIAL_FORMS": "0",
                "addons-MIN_NUM_FORMS": "0",
                "addons-MAX_NUM_FORMS": "1000",
            }
        )

        response = self.client.post(reverse("admin-venue-create"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("slug", response.context["form"].errors)
        self.assertIn(
            "Slug venue ini sudah digunakan.", response.context["form"].errors["slug"][0]
        )
