from django.contrib import admin

from addons.models import AddOn

from .models import Category, Venue, VenueAvailability


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


class AddOnInline(admin.TabularInline):
    model = AddOn
    extra = 1


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "price_per_hour", "category")
    list_filter = ("city", "category")
    search_fields = ("name", "city")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AddOnInline]


@admin.register(VenueAvailability)
class VenueAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("venue", "start_datetime", "end_datetime")
    list_filter = ("venue",)
