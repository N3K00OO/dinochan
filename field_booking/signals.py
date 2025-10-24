"""Signals ensuring booking payments stay in sync."""
from __future__ import annotations

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import Booking


@receiver(post_save, sender=Booking)
def ensure_payment_for_booking(sender, instance: Booking, created: bool, **kwargs):
    """Ensure a payment record exists whenever a booking is created."""

    payment = instance.ensure_payment()
    if not created and payment.total_amount != instance.total_cost:
        payment.total_amount = instance.total_cost
        payment.save(update_fields=["total_amount", "updated_at"])


@receiver(m2m_changed, sender=Booking.addons.through)
def update_payment_on_addons(sender, instance: Booking, action: str, **kwargs):
    """Recalculate payment totals when add-ons are modified."""

    if action in {"post_add", "post_remove", "post_clear"}:
        payment = instance.ensure_payment()
        if payment.total_amount != instance.total_cost:
            payment.total_amount = instance.total_cost
            payment.save(update_fields=["total_amount", "updated_at"])
