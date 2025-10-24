"""Booking and payment forms."""
from __future__ import annotations

from datetime import datetime

from django import forms
from django.utils import timezone

from .models import Booking, Payment


def _default_opening_hours() -> tuple[datetime.time, datetime.time]:
    start = datetime.min.time()
    end = datetime.max.time().replace(microsecond=0)
    return start, end


def _resolve_venue_hours(venue) -> tuple[datetime.time, datetime.time]:
    if venue is None:
        return _default_opening_hours()
    start_time = getattr(venue, "available_start_time", None)
    end_time = getattr(venue, "available_end_time", None)
    if start_time is None or end_time is None:
        return _default_opening_hours()
    return start_time, end_time


def _ensure_timezone(value: datetime) -> datetime:
    if timezone.is_naive(value):
        current_timezone = timezone.get_current_timezone()
        try:
            return timezone.make_aware(value, timezone=current_timezone)
        except Exception:
            try:
                return timezone.make_aware(value, timezone=current_timezone, is_dst=True)
            except Exception:
                return value
    return value


def normalize_booking_window(start_date, end_date, venue) -> tuple[datetime, datetime]:
    """Return timezone-aware datetimes spanning the venue's booking window."""

    start_time, end_time = _resolve_venue_hours(venue)
    start = _ensure_timezone(datetime.combine(start_date, start_time))
    end_anchor = end_date
    if end_time <= start_time:
        end_anchor = end_date + timedelta(days=1)
    end = _ensure_timezone(datetime.combine(end_anchor, end_time))
    return start, end


def ensure_no_overlap(venue, start: datetime, end: datetime, instance_pk: Optional[int] = None) -> None:
    if venue is None:
        return
    overlapping = (
        Booking.objects.filter(venue=venue, status__in=Booking.ACTIVE_STATUSES)
        .filter(start_datetime__lt=end, end_datetime__gt=start)
    )
    if instance_pk is not None:
        overlapping = overlapping.exclude(pk=instance_pk)
    if overlapping.exists():
        raise forms.ValidationError("This venue is already booked for the selected dates.")


class BookingForm(forms.ModelForm):
    """Form used to capture booking details from the user."""

    start_datetime = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
            }
        )
    )
    end_datetime = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
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
        if "start_datetime" in self.fields:
            self.fields["start_datetime"].label = "Start date"
        if "end_datetime" in self.fields:
            self.fields["end_datetime"].label = "End date"
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
        start_date = cleaned_data.get("start_datetime")
        end_date = cleaned_data.get("end_datetime")

        if start_date and end_date:
            start_time = getattr(self.venue, "available_start_time", None)
            end_time = getattr(self.venue, "available_end_time", None)

            if start_time is None or end_time is None:
                start_time = datetime.min.time()
                end_time = datetime.max.time().replace(microsecond=0)

            start = datetime.combine(start_date, start_time)
            end = datetime.combine(end_date, end_time)

            current_timezone = timezone.get_current_timezone()
            if timezone.is_naive(start):
                try:
                    start = timezone.make_aware(start, timezone=current_timezone)
                except Exception:
                    try:
                        start = timezone.make_aware(start, timezone=current_timezone, is_dst=True)
                    except Exception:
                        # Timezone support disabled or timezone not found; keep naive datetime.
                        pass
            if timezone.is_naive(end):
                try:
                    end = timezone.make_aware(end, timezone=current_timezone)
                except Exception:
                    try:
                        end = timezone.make_aware(end, timezone=current_timezone, is_dst=True)
                    except Exception:
                        pass

            cleaned_data["start_datetime"] = start
            cleaned_data["end_datetime"] = end

            if end.date() < start.date():
                raise forms.ValidationError("End date must be on or after the start date.")

            if end <= start:
                raise forms.ValidationError(
                    "Selected dates must fall within the venue's available hours."
                )

        if start_date and end_date and self.venue is not None:
            start = cleaned_data.get("start_datetime")
            end = cleaned_data.get("end_datetime")
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
                    "This venue is already booked for the selected dates."
                )

            if self.venue is not None:
                ensure_no_overlap(self.venue, start, end, self.instance.pk)
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


class BookingAdminForm(forms.ModelForm):
    """Admin form mirroring the public booking experience with date-only inputs."""

    start_datetime = forms.DateField(widget=AdminDateWidget(), label="Start date")
    end_datetime = forms.DateField(widget=AdminDateWidget(), label="End date")

    class Meta:
        model = Booking
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        venue = cleaned_data.get("venue") or getattr(self.instance, "venue", None)
        start_date = cleaned_data.get("start_datetime")
        end_date = cleaned_data.get("end_datetime")

        if start_date and end_date:
            start, end = normalize_booking_window(start_date, end_date, venue)
            cleaned_data["start_datetime"] = start
            cleaned_data["end_datetime"] = end

            if end_date < start_date:
                raise forms.ValidationError("End date must be on or after the start date.")

            ensure_no_overlap(venue, start, end, self.instance.pk)

        return cleaned_data
