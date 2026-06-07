from django.contrib import admin
from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "subproject",
        "created_by",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    autocomplete_fields = (
        "subproject",
        "created_by",
        "members",
    )

    filter_horizontal = (
        "members",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )