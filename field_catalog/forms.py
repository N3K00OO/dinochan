from __future__ import annotations

from django import forms
from django.db.models import Case, IntegerField, When

from field_management.constants import CATEGORY_SLUG_SEQUENCE
from field_management.models import Category, Venue


class SearchFilterForm(forms.Form):
    """Form displayed in navigation for quick searching."""

    city = forms.ChoiceField(
        required=False,
        choices=(),
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 backdrop-blur",
            }
        ),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.none(),
        empty_label="All categories",
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 backdrop-blur",
            }
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 placeholder:text-white/60 backdrop-blur",
                "placeholder": "Max Price",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        preferred_city_order = [
            "Jakarta",
            "Bandung",
            "Tangerang",
            "Yogyakarta",
            "Surabaya",
            "Makassar",
            "Denpasar",
            "Palembang",
            "Semarang",
            "Medan",
        ]

        city_choices = [("", "All cities")]
        for city in preferred_city_order:
            city_choices.append((city, city))

        remaining_cities = (
            Venue.objects.exclude(city__in=preferred_city_order)
            .order_by("city")
            .values_list("city", flat=True)
            .distinct()
        )
        for city in remaining_cities:
            if city:
                city_choices.append((city, city))

        self.fields["city"].choices = city_choices

        order_expression = Case(
            *[When(slug=slug, then=position) for position, slug in enumerate(CATEGORY_SLUG_SEQUENCE)],
            default=len(CATEGORY_SLUG_SEQUENCE),
            output_field=IntegerField(),
        )
        self.fields["category"].queryset = (
            Category.objects.filter(slug__in=CATEGORY_SLUG_SEQUENCE)
            .annotate(_display_order=order_expression)
            .order_by("_display_order")
        )
