"""Routes for wishlist and review interactions."""
from django.urls import path

from .views import WishlistToggleView, WishlistView, wishlist_toggle

urlpatterns = [
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/toggle/<int:pk>/", WishlistToggleView.as_view(), name="wishlist-toggle"),
    path("api/wishlist/<int:pk>/toggle/", wishlist_toggle, name="wishlist-toggle-api"),
]
