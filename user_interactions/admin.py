from django.contrib import admin

from .models import Review, Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "venue", "created_at")
    list_filter = ("user",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("venue", "user", "rating", "created_at")
    list_filter = ("rating", "venue")
    search_fields = ("comment", "venue__name", "user__username")
