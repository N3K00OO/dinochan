"""Root URL configuration for the venue booking project."""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("accounts.urls")),
    path("workspace/", include("field_management.urls")),
    path("", include("field_catalog.urls")),
    path("", include("field_booking.urls")),
    path("", include("user_interactions.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.ico")),
]
