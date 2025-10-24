"""Forms for managing venues."""
from __future__ import annotations

from django import forms
from django.db.models import Case, IntegerField, When
from django.utils.text import slugify

from field_booking.models import Booking

from .constants import CATEGORY_SLUG_SEQUENCE
from .models import Category, Venue


class VenueForm(forms.ModelForm):
    """Admin form to manage venues."""

    class Meta:
        model = Venue
        fields = (
            "category",
            "name",
            "slug",
            "description",
            "location",
            "city",
            "address",
            "price_per_hour",
            "capacity",
            "facilities",
            "image_url",
            "available_start_time",
            "available_end_time",
        )
        widgets = {
            "category": forms.Select(
                attrs={
                    "class": "custom-select w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 backdrop-blur",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 4,
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 placeholder-white/60 backdrop-blur",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 3,
                }
            ),
            "price_per_hour": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 placeholder-white/60 backdrop-blur",
                    "step": "0.01",
                }
            ),
            "capacity": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "min": 1,
                }
            ),
            "facilities": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 3,
                }
            ),
            "image_url": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/50 backdrop-blur",
                }
            ),
            "available_start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/60 backdrop-blur",
                }
            ),
            "available_end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/60 backdrop-blur",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Nama lapangan"
        self.fields["location"].label = "Lokasi"
        self.fields["city"].label = "Kota"
        self.fields["price_per_hour"].label = "Rentang harga"
        self.fields["price_per_hour"].help_text = "Masukkan harga sewa per jam."
        self.fields["facilities"].label = "Fasilitas tambahan"
        self.fields["facilities"].help_text = "Pisahkan setiap fasilitas dengan koma."
        self.fields["slug"].required = False

        order_expression = Case(
            *[When(slug=slug, then=position) for position, slug in enumerate(CATEGORY_SLUG_SEQUENCE)],
            default=len(CATEGORY_SLUG_SEQUENCE),
            output_field=IntegerField(),
        )
        self.fields["category"].queryset = (
            Category.objects.annotate(_display_order=order_expression).order_by("_display_order", "name")
        )
        self.fields["category"].empty_label = "Pilih kategori olahraga"

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")
        base = slug or name
        if base:
            normalized_slug = slugify(base)
            existing = Venue.objects.filter(slug=normalized_slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    "Slug venue ini sudah digunakan. Gunakan nama atau slug lain."
                )
            return normalized_slug
        return slug


class BookingDecisionForm(forms.Form):
    """Validate admin actions performed on booking approvals."""

    APPROVE = "approve"
    CANCEL = "cancel"

    DECISION_CHOICES = (
        (APPROVE, "Approve"),
        (CANCEL, "Cancel"),
    )

    booking_id = forms.IntegerField(widget=forms.HiddenInput)
    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking: Booking | None = None

    def clean(self):
        cleaned_data = super().clean()
        booking_id = cleaned_data.get("booking_id")
        decision = cleaned_data.get("decision")
        if booking_id is None or decision is None:
            return cleaned_data

        try:
            booking = Booking.objects.select_related("payment").get(pk=booking_id)
        except Booking.DoesNotExist as exc:  # pragma: no cover - defensive guard
            raise forms.ValidationError("Booking tidak ditemukan.") from exc

        if booking.status != Booking.STATUS_PENDING:
            raise forms.ValidationError("Booking ini sudah diproses.")

        self.booking = booking
        return cleaned_data

    def apply_decision(self, approver) -> tuple[Booking, str]:
        """Persist the selected decision and return the updated booking."""

        if not self.is_valid() or self.booking is None:
            raise ValueError("Form harus divalidasi sebelum diproses.")

        decision = self.cleaned_data["decision"]
        booking = self.booking

        if decision == self.APPROVE:
            booking.approve(approver)
        elif decision == self.CANCEL:
            booking.cancel()
            if hasattr(booking, "payment"):
                booking.payment.status = "waiting"
                booking.payment.save(update_fields=["status", "updated_at"])
        else:  # pragma: no cover - guarded by ChoiceField
            raise ValueError("Keputusan tidak valid.")

        return booking, decision
