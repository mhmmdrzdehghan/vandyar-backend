from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )