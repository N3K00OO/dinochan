"""Forms for user interaction features."""
from __future__ import annotations

from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Form that captures a venue review."""

    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white backdrop-blur",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/40 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 4,
                }
            ),
        }
