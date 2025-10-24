from django.apps import AppConfig


class FieldBookingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "field_booking"
    verbose_name = "Field Booking"

    def ready(self):  # pragma: no cover
        from . import signals  # noqa: F401
