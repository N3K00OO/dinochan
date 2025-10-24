"""Models for managing sports venues."""
from __future__ import annotations

from decimal import Decimal
from datetime import time

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class TimestampedModel(models.Model):
    """Abstract base model providing timestamp fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimestampedModel):
    """Represents a sports venue category."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Venue(TimestampedModel):
    """Venue model holding primary information."""

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="venues")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField()
    location = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=1)
    facilities = models.TextField(help_text="Comma separated facilities list.")
    image_url = models.URLField(blank=True)
    available_start_time = models.TimeField(default=time(7, 0))
    available_end_time = models.TimeField(default=time(22, 0))

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name

    @property
    def facilities_list(self) -> list[str]:
        return [facility.strip() for facility in self.facilities.split(",") if facility.strip()]

    def hourly_total(self, hours: int) -> Decimal:
        return self.price_per_hour * Decimal(hours)


class VenueAvailability(TimestampedModel):
    """Represents a block of time when the venue is available for booking."""

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="availabilities")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        ordering = ["start_datetime"]
        verbose_name_plural = "Venue availabilities"

    def clean(self):  # pragma: no cover - requires Django validation
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be greater than start datetime")
