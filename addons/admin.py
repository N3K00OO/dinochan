from django.contrib import admin

from .models import AddOn


@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ("name", "venue", "price", "updated_at")
    list_filter = ("venue",)
    search_fields = ("name", "venue__name")
