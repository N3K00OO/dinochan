"""Forms for managing add-on rentals."""
from __future__ import annotations

from django import forms

from .models import AddOn


class AddOnForm(forms.ModelForm):
    """Admin form to manage add-ons."""

    class Meta:
        model = AddOn
        fields = ("name", "description", "price")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-white placeholder-white/60 backdrop-blur",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "rows": 2,
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder-white/60 backdrop-blur",
                    "step": "0.01",
                    "min": 0,
                }
            ),
        }
