from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from addons.models import AddOn
from field_booking.models import Booking
from field_management.models import Category, Venue


class BookingFlowTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="booker",
            email="booker@example.com",
            password="secret123",
        )
        self.admin = get_user_model().objects.create_user(
            username="approver",
            email="approver@example.com",
            password="secret123",
            is_staff=True,
        )
        self.category = Category.objects.create(name="Stadium")
        self.venue = Venue.objects.create(
            category=self.category,
            name="Skyline Arena",
            description="Indoor multi-purpose arena.",
            location="Central",
            city="Metropolis",
            address="1 Arena Way",
            price_per_hour="150000.00",
            capacity=1500,
            facilities="Lighting, Seating",
            image_url="https://example.com/arena.jpg",
        )
        self.addon = AddOn.objects.create(
            venue=self.venue,
            name="Premium lighting",
            description="Enhanced lighting package",
            price="50000.00",
        )

    def test_user_can_submit_booking_request(self) -> None:
        self.client.force_login(self.user)
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        response = self.client.post(
            reverse("venue-detail", kwargs={"slug": self.venue.slug}),
            {
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
                "notes": "Looking forward to the event.",
                "addons": [str(self.addon.pk)],
            },
        )
        self.assertRedirects(response, reverse("booked-places"))
        booking = Booking.objects.get(user=self.user, venue=self.venue)
        self.assertEqual(booking.status, Booking.STATUS_PENDING)
        self.assertTrue(booking.addons.filter(pk=self.addon.pk).exists())
        self.assertTrue(hasattr(booking, "payment"))
        self.assertEqual(booking.payment.total_amount, booking.total_cost)

    def test_booking_requires_distinct_times(self) -> None:
        self.client.force_login(self.user)
        start = timezone.now() + timedelta(days=2)
        response = self.client.post(
            reverse("venue-detail", kwargs={"slug": self.venue.slug}),
            {
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": start.strftime("%Y-%m-%dT%H:%M"),
            },
            follow=True,
        )
        self.assertRedirects(
            response, reverse("venue-detail", kwargs={"slug": self.venue.slug})
        )
        self.assertEqual(Booking.objects.count(), 0)
        messages = list(response.context["messages"])
        self.assertTrue(any("Unable to create booking" in str(message) for message in messages))

    def test_user_can_pay_once_booking_is_approved(self) -> None:
        self.client.force_login(self.user)
        start = timezone.now() + timedelta(days=3)
        end = start + timedelta(hours=1)
        self.client.post(
            reverse("venue-detail", kwargs={"slug": self.venue.slug}),
            {
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
            },
        )
        booking = Booking.objects.get(user=self.user, venue=self.venue)
        pending_response = self.client.get(reverse("payment", args=[booking.pk]))
        self.assertRedirects(pending_response, reverse("wishlist"))

        booking.approve(self.admin)
        booking.refresh_from_db()

        payment_page = self.client.get(reverse("payment", args=[booking.pk]))
        self.assertEqual(payment_page.status_code, 200)
        confirm_response = self.client.post(
            reverse("payment", args=[booking.pk]),
            {"method": "gopay"},
        )
        self.assertRedirects(confirm_response, reverse("booked-places"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)
        self.assertEqual(booking.payment.status, "confirmed")
        self.assertEqual(booking.payment.method, "gopay")

    def test_approved_booking_visible_on_booked_places(self) -> None:
        self.client.force_login(self.user)
        start = timezone.now() + timedelta(days=5)
        end = start + timedelta(hours=2)
        self.client.post(
            reverse("venue-detail", kwargs={"slug": self.venue.slug}),
            {
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
            },
        )
        booking = Booking.objects.get(user=self.user, venue=self.venue)
        booking.approve(self.admin)
        booking.refresh_from_db()

        response = self.client.get(reverse("booked-places"))
        self.assertContains(response, booking.venue.name)
        self.assertContains(response, "Awaiting payment")
        self.assertContains(response, reverse("payment", args=[booking.pk]))

    def test_user_can_cancel_confirmed_booking(self) -> None:
        self.client.force_login(self.user)
        start = timezone.now() + timedelta(days=4)
        end = start + timedelta(hours=1)
        self.client.post(
            reverse("venue-detail", kwargs={"slug": self.venue.slug}),
            {
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
            },
        )

        booking = Booking.objects.get(user=self.user, venue=self.venue)
        booking.approve(self.admin)
        booking.refresh_from_db()

        self.client.post(reverse("payment", args=[booking.pk]), {"method": "gopay"})
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)
        self.assertEqual(booking.payment.status, "confirmed")

        response = self.client.post(reverse("booking-cancel", args=[booking.pk]))
        self.assertRedirects(response, reverse("booked-places"))

        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CANCELLED)
        self.assertEqual(booking.payment.status, "waiting")
