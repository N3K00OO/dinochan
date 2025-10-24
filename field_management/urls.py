"""Admin URLs for venue management."""
from django.urls import path

from .views import (
    AdminBookingApprovalView,
    AdminDashboardView,
    AdminVenueCreateView,
    AdminVenueDeleteView,
    AdminVenueListView,
    AdminVenueUpdateView,
)

urlpatterns = [
    path("", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("bookings/", AdminBookingApprovalView.as_view(), name="admin-bookings"),
    path("venues/", AdminVenueListView.as_view(), name="admin-venues"),
    path("venues/add/", AdminVenueCreateView.as_view(), name="admin-venue-create"),
    path("venues/<int:pk>/edit/", AdminVenueUpdateView.as_view(), name="admin-venue-edit"),
    path("venues/<int:pk>/delete/", AdminVenueDeleteView.as_view(), name="admin-venue-delete"),
]
