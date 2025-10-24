"""Routes for booking workflows."""
from django.urls import path

from .views import BookingCancelView, BookingPaymentView, BookedPlacesView

urlpatterns = [
    path("bookings/", BookedPlacesView.as_view(), name="booked-places"),
    path("bookings/<int:pk>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),
    path("booking/<int:pk>/payment/", BookingPaymentView.as_view(), name="payment"),
]
