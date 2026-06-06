from django.contrib import admin
from .models import Project, SubProject


class SubProjectInline(admin.TabularInline):
    model = SubProject
    extra = 0
    fields = (
        "title",
        "description",
        "created_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "created_by",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "created_by__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [SubProjectInline]

    ordering = ("-created_at",)


@admin.register(SubProject)
class SubProjectAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "project",
        "created_by",
        "created_at",
    )

    list_filter = (
        "project",
        "created_at",
    )

    search_fields = (
        "title",
        "project__title",
        "created_by__username",
    )

    filter_horizontal = (
        "managers",
        "members",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)
