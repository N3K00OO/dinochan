"""Booking and payment forms."""
from __future__ import annotations

from django import forms

from .models import Booking, Payment


class BookingForm(forms.ModelForm):
    """Form used to capture booking details from the user."""

    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
            }
        )
    )
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
            }
        )
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                "rows": 3,
            }
        ),
    )

    def __init__(self, *args, venue=None, **kwargs):
        self.venue = venue
        super().__init__(*args, **kwargs)
        addons_field = self.fields.get("addons")
        if addons_field is not None:
            existing_classes = addons_field.widget.attrs.get("class", "")
            addons_field.widget.attrs["class"] = (
                f"{existing_classes} addon-option__input".strip()
            )
            addons_field.widget.attrs.setdefault("data-addon-input", "true")
            if venue is not None:
                addons_field.queryset = venue.addons.all()

                def _label(addon):
                    return f"{addon.name} • Rp {addon.price}"

                addons_field.label_from_instance = _label

    class Meta:
        model = Booking
        fields = ("start_datetime", "end_datetime", "notes", "addons")
        widgets = {
            "addons": forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_datetime")
        end = cleaned_data.get("end_datetime")
        if start and end and start >= end:
            raise forms.ValidationError("End time must be after the start time.")
        if start and end and self.venue is not None:
            overlapping = (
                Booking.objects.filter(
                    venue=self.venue,
                    status__in=Booking.ACTIVE_STATUSES,
                )
                .filter(start_datetime__lt=end, end_datetime__gt=start)
                .exclude(pk=self.instance.pk)
            )
            if overlapping.exists():
                raise forms.ValidationError(
                    "This venue is already booked for the selected time range."
                )
        return cleaned_data


class PaymentForm(forms.ModelForm):
    """Form used to confirm payment method."""

    class Meta:
        model = Payment
        fields = ("method",)
        widgets = {
            "method": forms.RadioSelect(
                attrs={
                    "class": "flex flex-col gap-3 text-white",
                }
            )
        }
