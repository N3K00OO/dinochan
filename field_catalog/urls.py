"""Public catalog URLs."""
from django.urls import path

from .views import CatalogView, HomeView, VenueDetailView, catalog_filter

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("catalog/", CatalogView.as_view(), name="catalog"),
    path("api/catalog/filter/", catalog_filter, name="catalog-filter"),
    path("venue/<slug:slug>/", VenueDetailView.as_view(), name="venue-detail"),
]
