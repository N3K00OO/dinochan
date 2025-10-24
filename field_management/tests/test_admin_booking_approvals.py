"""Tests for the admin booking approvals workflow."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from field_booking.models import Booking
from field_management.models import Category, Venue


class AdminBookingApprovalViewTests(TestCase):
    """Ensure administrators can process booking decisions."""

    def setUp(self) -> None:
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username="approver",
            email="approver@example.com",
            password="secret123",
            is_staff=True,
        )
        self.user = user_model.objects.create_user(
            username="booker",
            email="booker@example.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="Arena")
        self.venue = Venue.objects.create(
            category=self.category,
            name="Sunrise Field",
            description="Outdoor field for sports events.",
            location="Central",
            city="Metropolis",
            address="123 Main St",
            price_per_hour=Decimal("120000.00"),
            capacity=100,
            facilities="Lighting, Seating",
            image_url="https://example.com/venue.jpg",
        )

    def _create_booking(self) -> Booking:
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        return Booking.objects.create(
            user=self.user,
            venue=self.venue,
            start_datetime=start,
            end_datetime=end,
            notes="Need setup 1 hour before.",
        )

    def test_admin_can_approve_pending_booking(self) -> None:
        booking = self._create_booking()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("admin-bookings"),
            {"booking_id": booking.pk, "decision": "approve"},
        )

        self.assertRedirects(response, reverse("admin-bookings"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_ACTIVE)
        self.assertIsNotNone(booking.approved_at)
        self.assertEqual(booking.approved_by, self.admin)
        self.assertTrue(hasattr(booking, "payment"))
        self.assertEqual(booking.payment.status, "waiting")

    def test_admin_can_cancel_pending_booking(self) -> None:
        booking = self._create_booking()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("admin-bookings"),
            {"booking_id": booking.pk, "decision": "cancel"},
        )

        self.assertRedirects(response, reverse("admin-bookings"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CANCELLED)
        self.assertIsNone(booking.approved_at)
        self.assertIsNone(booking.approved_by)
        self.assertTrue(hasattr(booking, "payment"))
        self.assertEqual(booking.payment.status, "waiting")

    def test_missing_booking_id_returns_error(self) -> None:
        booking = self._create_booking()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("admin-bookings"),
            {"decision": "approve"},
            follow=True,
        )

        self.assertRedirects(response, reverse("admin-bookings"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_PENDING)
        messages = list(response.context["messages"])
        self.assertTrue(any("This field is required" in str(message) for message in messages))

    def test_cannot_process_already_handled_booking(self) -> None:
        booking = self._create_booking()
        booking.cancel()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("admin-bookings"),
            {"booking_id": booking.pk, "decision": "approve"},
            follow=True,
        )

        self.assertRedirects(response, reverse("admin-bookings"))
        messages = list(response.context["messages"])
        self.assertTrue(any("sudah diproses" in str(message) for message in messages))
