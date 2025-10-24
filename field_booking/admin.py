from django.contrib import admin

from .models import Booking, Payment


class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("venue", "user", "start_datetime", "end_datetime")
    list_filter = ("venue", "user")
    search_fields = ("venue__name", "user__username")
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "method", "status", "total_amount", "updated_at")
    list_filter = ("status", "method")
    search_fields = ("reference_code",)
