from django.contrib import admin

from .models import (
    Task,
    Status,
    TaskRoutine,
    TaskAssignment,
    TaskAttachment,
    CheckList
)


# ==========================
# Inlines
# ==========================

class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 0


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = (
        "file_name",
        "file_size",
        "file_type",
        "uploaded_by",
        "created_at",
    )


class CheckListInline(admin.TabularInline):
    model = CheckList
    extra = 0


class TaskRoutineInline(admin.StackedInline):
    model = TaskRoutine
    extra = 0
    max_num = 1


# ==========================
# Task
# ==========================

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "priority",
        "created_by",
        "planned_start_at",
        "deadline",
        "created_at",
        "is_routine"

    )

    list_filter = (
        "priority",
        "created_at",
        "deadline",
        "is_routine"

    )

    search_fields = (
        "title",
        "description",
        "created_by__username",
        "created_by__email",
    )

    autocomplete_fields = (
        "created_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"

    inlines = [
        TaskRoutineInline,
        TaskAssignmentInline,
        TaskAttachmentInline,
        CheckListInline,
    ]


# ==========================
# Status
# ==========================

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "created_at",
    )

    search_fields = (
        "title",
    )


# ==========================
# TaskRoutine
# ==========================

@admin.register(TaskRoutine)
class TaskRoutineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "period",
        "start_date",
        "end_date",
        "next_run_at",
        "is_active",
    )

    list_filter = (
        "period",
        "is_active",
    )

    search_fields = (
        "task__title",
    )

    autocomplete_fields = (
        "task",
    )


# ==========================
# TaskAssignment
# ==========================

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "assigned_to",
        "status",
        "quality_rate",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "task__title",
        "assigned_to__username",
        "assigned_to__email",
    )

    autocomplete_fields = (
        "task",
        "assigned_to",
        "status",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================
# TaskAttachment
# ==========================

@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file_name",
        "task",
        "uploaded_by",
        "file_size",
        "file_type",
        "created_at",
    )

    list_filter = (
        "file_type",
        "created_at",
    )

    search_fields = (
        "file_name",
        "task__title",
        "uploaded_by__username",
    )

    autocomplete_fields = (
        "task",
        "uploaded_by",
    )

    readonly_fields = (
        "file_path",
        "file_size",
        "file_type",
        "created_at",
        "updated_at",
    )


# ==========================
# CheckList
# ==========================

@admin.register(CheckList)
class CheckListAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "title",
        "is_done",
        "created_at",
    )

    list_filter = (
        "is_done",
        "created_at",
    )

    search_fields = (
        "title",
        "task__title",
    )

    autocomplete_fields = (
        "task",
    )