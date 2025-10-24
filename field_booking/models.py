"""Models powering the booking flow."""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from field_management.models import Venue


class Booking(models.Model):
    """Captures a user's booking details."""

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending approval"),
        (STATUS_ACTIVE, "Reserved"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    ACTIVE_STATUSES = (STATUS_PENDING, STATUS_ACTIVE, STATUS_CONFIRMED)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="bookings")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    addons = models.ManyToManyField("addons.AddOn", related_name="bookings", blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_bookings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_datetime"]

    def clean(self):  # pragma: no cover - requires Django validation
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be greater than start datetime")

    @property
    def duration_hours(self) -> int:
        delta = self.end_datetime - self.start_datetime
        return int(delta.total_seconds() // 3600)

    @property
    def addons_total(self) -> Decimal:
        return sum((addon.price for addon in self.addons.all()), Decimal("0"))

    @property
    def base_cost(self) -> Decimal:
        return self.venue.hourly_total(self.duration_hours)

    @property
    def total_cost(self) -> Decimal:
        return self.base_cost + self.addons_total

    @property
    def is_admin_approved(self) -> bool:
        return self.approved_at is not None

    def ensure_payment(self) -> "Payment":
        """Return a payment record for this booking, creating or updating as needed."""

        from uuid import uuid4

        payment, created = Payment.objects.get_or_create(
            booking=self,
            defaults={
                "method": "qris",
                "status": "waiting",
                "total_amount": self.total_cost,
                "deposit_amount": Decimal("10000"),
                "reference_code": uuid4().hex[:12].upper(),
            },
        )
        if not created and payment.total_amount != self.total_cost:
            payment.total_amount = self.total_cost
            payment.save(update_fields=["total_amount", "updated_at"])
        return payment

    def approve(self, user) -> None:
        """Mark the booking as approved by an administrator."""

        self.status = self.STATUS_ACTIVE
        self.approved_at = timezone.now()
        self.approved_by = user
        self.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])
        payment = self.ensure_payment()
        if payment.status != "waiting":
            payment.status = "waiting"
            payment.save(update_fields=["status", "updated_at"])

    def cancel(self, save: bool = True) -> None:
        """Cancel the booking and clear any approval metadata."""

        self.status = self.STATUS_CANCELLED
        self.approved_at = None
        self.approved_by = None
        if save:
            self.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])


class Payment(models.Model):
    """Tracks payment status for a booking."""

    METHOD_CHOICES = [
        ("qris", "QRIS"),
        ("gopay", "GoPay"),
    ]

    STATUS_CHOICES = [
        ("waiting", "Waiting for confirmation"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("10000"))
    reference_code = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Payment {self.reference_code} ({self.get_status_display()})"
