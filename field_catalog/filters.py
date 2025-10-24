from django import forms
from django.db.models import Case, IntegerField, When
import django_filters

from field_management.constants import CATEGORY_SLUG_SEQUENCE
from field_management.models import Category, Venue


class VenueFilter(django_filters.FilterSet):
    city = django_filters.ChoiceFilter(
        field_name="city",
        lookup_expr="exact",
        empty_label="All cities",
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 backdrop-blur",
            }
        ),
    )
    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=Category.objects.none(),
        empty_label="All categories",
        widget=forms.Select(
            attrs={
                "class": "custom-select w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 backdrop-blur",
            }
        ),
    )
    max_price = django_filters.NumberFilter(
        field_name="price_per_hour",
        lookup_expr="lte",
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-2xl border border-white/25 bg-slate-950/70 px-5 py-3 text-sm text-white/90 placeholder:text-white/60 backdrop-blur",
                "placeholder": "Max Price",
                "min": 0,
                "step": "0.01",
            }
        ),
    )

    class Meta:
        model = Venue
        fields = ["city", "category", "max_price"]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if queryset is None:
            queryset = Venue.objects.all()
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

        city_values = (
            self.queryset.order_by("city")
            .values_list("city", flat=True)
            .distinct()
        )
        city_choices = [("", "All cities")] + [
            (value, value) for value in city_values if value
        ]

        if "city" in self.filters:
            self.filters["city"].field.choices = city_choices
        if "city" in self.form.fields:
            self.form.fields["city"].choices = city_choices

        order_expression = Case(
            *[When(slug=slug, then=position) for position, slug in enumerate(CATEGORY_SLUG_SEQUENCE)],
            default=len(CATEGORY_SLUG_SEQUENCE),
            output_field=IntegerField(),
        )
        category_queryset = (
            Category.objects.filter(slug__in=CATEGORY_SLUG_SEQUENCE)
            .annotate(_display_order=order_expression)
            .order_by("_display_order")
        )
        if "category" in self.filters:
            self.filters["category"].field.queryset = category_queryset
        if "category" in self.form.fields:
            self.form.fields["category"].queryset = category_queryset
