"""Context processors for catalog module."""
from __future__ import annotations

from .forms import SearchFilterForm


def global_filters(request):
    """Provide the search filter form globally for navigation search bars."""

    return {
        "global_filter_form": SearchFilterForm(request.GET or None),
    }
