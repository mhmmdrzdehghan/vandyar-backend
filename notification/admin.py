from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "recipient",
        "actor",
        "content_type",
        "object_id",
        "created_at",
    )

    list_filter = (
        "content_type",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "title",
        "message",
        "recipient__email",
        "recipient__username",
        "actor__email",
        "actor__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "recipient",
        "actor",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "recipient",
                    "actor",
                    "title",
                    "message",
                )
            },
        ),
        (
            "مرجع",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )