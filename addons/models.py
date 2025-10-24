"""Models for optional sports equipment add-ons."""
from __future__ import annotations

from django.db import models


class AddOn(models.Model):
    """Optional add-ons that can be purchased with a booking."""

    venue = models.ForeignKey(
        "field_management.Venue",
        on_delete=models.CASCADE,
        related_name="addons",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} ({self.venue.name})"
