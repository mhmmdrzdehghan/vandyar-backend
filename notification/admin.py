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

    ordering = (
        "-created_at",
    )

    autocomplete_fields = (
        "recipient",
        "actor",
    )

    fieldsets = (
        (
            "Users",
            {
                "fields": (
                    "recipient",
                    "actor",
                )
            },
        ),
        (
            "Notification",
            {
                "fields": (
                    "title",
                    "message",
                )
            },
        ),
        (
            "Reference Object",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )