"""Views handling booking and payment flows."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from .forms import PaymentForm
from .models import Booking, Payment


class BookingCancelView(LoginRequiredMixin, View):
    """Allow a user to cancel their own booking."""

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        booking = get_object_or_404(Booking.objects.select_related("payment"), pk=pk, user=request.user)
        if booking.status in {Booking.STATUS_COMPLETED, Booking.STATUS_CANCELLED}:
            messages.error(request, "This booking can no longer be cancelled.")
            return redirect("booked-places")
        booking.cancel()

        payment = None
        try:
            payment = booking.payment
        except Payment.DoesNotExist:
            # Ensure a payment record exists so the user can book again later.
            payment = booking.ensure_payment()

        if payment is not None:
            payment.status = "waiting"
            payment.save(update_fields=["status", "updated_at"])
        messages.success(request, "Booking cancelled successfully.")
        return redirect("booked-places")


class BookingPaymentView(LoginRequiredMixin, View):
    template_name = "booking_payment.html"

    def _get_booking(self, request: HttpRequest, pk: int) -> Booking:
        booking = get_object_or_404(
            Booking.objects.select_related("venue", "payment").prefetch_related("addons"), pk=pk, user=request.user
        )
        booking.ensure_payment()
        return booking

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        booking = self._get_booking(request, pk)
        if booking.status == Booking.STATUS_PENDING:
            messages.error(request, "This booking still requires admin approval before payment.")
            return redirect("wishlist")
        if booking.status in {Booking.STATUS_CANCELLED, Booking.STATUS_COMPLETED}:
            messages.error(request, "This booking can no longer be paid.")
            return redirect("booked-places")
        form = PaymentForm(instance=booking.payment)
        return render(request, self.template_name, {"booking": booking, "form": form})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        booking = self._get_booking(request, pk)
        if booking.status == Booking.STATUS_PENDING:
            messages.error(request, "This booking still requires admin approval before payment.")
            return redirect("wishlist")
        if booking.status in {Booking.STATUS_CANCELLED, Booking.STATUS_COMPLETED}:
            messages.error(request, "This booking can no longer be paid.")
            return redirect("booked-places")
        form = PaymentForm(request.POST, instance=booking.payment)
        if form.is_valid():
            payment: Payment = form.save(commit=False)
            payment.status = "confirmed"
            payment.save()
            booking.status = Booking.STATUS_CONFIRMED
            booking.save(update_fields=["status", "updated_at"])
            messages.success(request, "Payment completed! Your booking is confirmed.")
            return redirect("booked-places")
        messages.error(request, "Could not process the payment. Please try again.")
        return render(request, self.template_name, {"booking": booking, "form": form})


class BookedPlacesView(LoginRequiredMixin, ListView):
    """Display all bookings made by the current user."""

    template_name = "booked_places.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return (
            Booking.objects.filter(
                user=self.request.user,
                status__in=[
                    Booking.STATUS_ACTIVE,
                    Booking.STATUS_CONFIRMED,
                    Booking.STATUS_COMPLETED,
                ],
            )
            .select_related("venue")
            .prefetch_related("addons")
            .order_by("-start_datetime")
        )
