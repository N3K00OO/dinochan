"""Admin workspace views for managing venues."""
from __future__ import annotations

import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.forms import inlineformset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView

from accounts.forms import AdminCreationForm
from accounts.mixins import AdminRequiredMixin
from addons.forms import AddOnForm
from addons.models import AddOn
from field_booking.models import Booking, Payment

from .forms import BookingDecisionForm, VenueForm
from .models import Venue

AddOnFormSet = inlineformset_factory(Venue, AddOn, form=AddOnForm, extra=3, can_delete=True)

logger = logging.getLogger(__name__)


class AdminDashboardView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "admin/dashboard.html"
    form_class = AdminCreationForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        context.update(
            {
                "stats": {
                    "venues": Venue.objects.count(),
                    "bookings": Booking.objects.count(),
                    "payments": Payment.objects.count(),
                    "pending_bookings": Booking.objects.filter(status=Booking.STATUS_PENDING).count(),
                },
                "admins": user_model.objects.filter(is_staff=True).order_by("username"),
                "admin_form": kwargs.get("admin_form") or self.form_class(),
            }
        )
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New admin account created successfully.")
            return redirect("admin-dashboard")
        messages.error(request, "Unable to create admin. Please correct the errors below.")
        return self.render_to_response(self.get_context_data(admin_form=form))


class AdminVenueListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    model = Venue
    template_name = "admin/venue_list.html"
    context_object_name = "venues"
    paginate_by = 10
    ordering = ["name"]
    form_class = VenueForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.setdefault("venue_form", kwargs.get("venue_form") or self.form_class())
        context["show_create_modal"] = kwargs.get("show_create_modal") or self.request.GET.get("show") == "create"
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.has_perm("field_management.add_venue"):
            messages.error(request, "You do not have permission to create venues.")
            return redirect("admin-venues")

        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error(
                    "slug",
                    "Slug venue ini sudah digunakan. Gunakan nama atau slug lain.",
                )
            else:
                messages.success(request, "Venue created successfully.")
                return redirect("admin-venues")
        messages.error(request, "Please fix the errors below to create the venue.")
        self.object_list = self.get_queryset()
        return self.render_to_response(
            self.get_context_data(venue_form=form, show_create_modal=True)
        )


class AdminVenueCreateView(AdminRequiredMixin, LoginRequiredMixin, View):
    template_name = "admin/venue_form.html"
    success_url = reverse_lazy("admin-venues")

    def get(self, request: HttpRequest) -> HttpResponse:
        form = VenueForm()
        formset = AddOnFormSet(instance=Venue())
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.has_perm("field_management.add_venue"):
            messages.error(request, "You do not have permission to create venues.")
            return redirect(self.success_url)

        form = VenueForm(request.POST)
        formset = AddOnFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            try:
                venue = form.save()
            except IntegrityError:
                form.add_error(
                    "slug",
                    "Slug venue ini sudah digunakan. Gunakan nama atau slug lain.",
                )
            else:
                formset.instance = venue
                formset.save()
                messages.success(request, "Venue created successfully.")
                return redirect(self.success_url)
        messages.error(request, "Please fix the errors below to create the venue.")
        return render(request, self.template_name, {"form": form, "formset": formset})


class AdminVenueUpdateView(AdminRequiredMixin, LoginRequiredMixin, View):
    template_name = "admin/venue_form.html"
    success_url = reverse_lazy("admin-venues")

    def get_object(self, pk: int) -> Venue:
        return get_object_or_404(Venue, pk=pk)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        venue = self.get_object(pk)
        form = VenueForm(instance=venue)
        formset = AddOnFormSet(instance=venue)
        return render(request, self.template_name, {"form": form, "formset": formset, "venue": venue})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        venue = self.get_object(pk)
        form = VenueForm(request.POST, instance=venue)
        formset = AddOnFormSet(request.POST, instance=venue)
        if form.is_valid() and formset.is_valid():
            try:
                venue = form.save()
            except IntegrityError:
                form.add_error(
                    "slug",
                    "Slug venue ini sudah digunakan. Gunakan nama atau slug lain.",
                )
            else:
                formset.instance = venue
                formset.save()
                messages.success(request, "Venue updated successfully.")
                return redirect(self.success_url)
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"form": form, "formset": formset, "venue": venue})


class AdminVenueDeleteView(AdminRequiredMixin, LoginRequiredMixin, View):
    success_url = reverse_lazy("admin-venues")

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        if not request.user.has_perm("field_management.delete_venue"):
            messages.error(request, "You do not have permission to delete venues.")
            return redirect(self.success_url)

        venue = get_object_or_404(Venue, pk=pk)
        venue.delete()
        messages.success(request, "Venue deleted successfully.")
        return redirect(self.success_url)


class AdminBookingApprovalView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "admin/booking_approvals.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pending_bookings"] = (
            Booking.objects.select_related("venue", "user")
            .prefetch_related("addons")
            .filter(status=Booking.STATUS_PENDING)
            .order_by("start_datetime")
        )
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = BookingDecisionForm(request.POST)

        if not form.is_valid():
            error_messages = list(form.non_field_errors())
            for field_errors in form.errors.values():
                error_messages.extend(field_errors)
            if not error_messages:
                error_messages.append("Unable to process the booking request.")
            for error in error_messages:
                messages.error(request, error)
            return redirect("admin-bookings")

        _, decision = form.apply_decision(request.user)
        if decision == BookingDecisionForm.APPROVE:
            messages.success(request, "Booking approved successfully.")
        else:
            messages.success(request, "Booking request cancelled.")
        return redirect("admin-bookings")
