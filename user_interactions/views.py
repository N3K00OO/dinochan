"""Wishlist and review helper views."""
from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import Truncator
from django.views import View
from django.views.generic import ListView

from accounts.mixins import EnsureCsrfCookieMixin
from field_booking.models import Booking
from field_management.models import Venue

from .models import Wishlist


class WishlistView(EnsureCsrfCookieMixin, LoginRequiredMixin, ListView):
    template_name = "wishlist.html"
    context_object_name = "wishlists"

    def get_queryset(self):
        return (
            Wishlist.objects.filter(user=self.request.user)
            .select_related("venue", "venue__category")
            .prefetch_related("venue__addons")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["approved_bookings"] = (
            Booking.objects.filter(user=self.request.user, status=Booking.STATUS_ACTIVE)
            .select_related("venue")
            .prefetch_related("addons")
            .order_by("-start_datetime")
        )
        return context


class WishlistToggleView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore[override]
        venue = get_object_or_404(Venue, pk=kwargs["pk"])
        wishlisted = _toggle_wishlist_entry(request, venue)
        return _wishlist_response(request, venue, wishlisted)


@login_required
def wishlist_toggle(request: HttpRequest, pk: int) -> HttpResponse:
    venue = get_object_or_404(Venue, pk=pk)
    wishlisted = _toggle_wishlist_entry(request, venue)
    return _wishlist_response(request, venue, wishlisted)


def _toggle_wishlist_entry(request: HttpRequest, venue: Venue) -> bool:
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, venue=venue)
    if created:
        return True
    wishlist.delete()
    return False


def _request_wants_json(request: HttpRequest) -> bool:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return True
    accept = request.headers.get("accept", "")
    return "application/json" in accept


def _get_next_url(request: HttpRequest) -> str:
    fallback = reverse("wishlist")
    candidate = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
    )
    if not candidate and request.content_type and "application/json" in request.content_type:
        try:
            payload = json.loads(request.body.decode() or "{}")
        except (TypeError, ValueError, JSONDecodeError):
            payload = {}
        candidate = payload.get("next")
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return fallback


def _wishlist_response(request: HttpRequest, venue: Venue, wishlisted: bool) -> HttpResponse:
    if _request_wants_json(request):
        return JsonResponse(_build_wishlist_response(request, venue, wishlisted))
    _add_wishlist_message(request, venue, wishlisted)
    return redirect(_get_next_url(request))


def _add_wishlist_message(request: HttpRequest, venue: Venue, wishlisted: bool) -> None:
    if wishlisted:
        messages.success(request, f"Added {venue.name} to your wishlist.")
    else:
        messages.info(request, f"Removed {venue.name} from your wishlist.")


def _build_wishlist_response(request: HttpRequest, venue: Venue, wishlisted: bool) -> dict[str, Any]:
    description = Truncator(venue.description or "").chars(120)
    venue_data = {
        "id": str(venue.pk),
        "name": venue.name,
        "city": venue.city,
        "category": venue.category.name if venue.category else "",
        "price": str(venue.price_per_hour),
        "url": reverse("venue-detail", kwargs={"slug": venue.slug}),
        "image": venue.image_url,
        "description": description,
        "toggle_url": reverse("wishlist-toggle-api", kwargs={"pk": venue.pk}),
    }
    response: dict[str, Any] = {
        "wishlisted": wishlisted,
        "wishlist_count": Wishlist.objects.filter(user=request.user).count(),
        "venue": venue_data,
        "wishlist_item_html": None,
    }
    if wishlisted:
        response["wishlist_item_html"] = render_to_string(
            "partials/wishlist_card.html",
            {
                "venue": venue,
                "wishlist_description": description,
                "wishlist_next_url": _get_next_url(request),
            },
            request=request,
        )
    return response
