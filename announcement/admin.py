# Register your models here.
from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "is_active",
        "recipient_count",
        "start_at",
        "end_at",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
        "start_at",
        "end_at",
    )

    search_fields = (
        "title",
        "message",
        "recipients__username",
        "recipients__email",
    )

    filter_horizontal = (
        "recipients",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    def recipient_count(self, obj):
        return obj.recipients.count()