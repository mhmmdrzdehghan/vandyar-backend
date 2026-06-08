from django.contrib import admin
from .models import Task, Status, TaskRoutine, TaskAttachment, CheckList


# ------------------------
# Status
# ------------------------
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)
    ordering = ("id",)


# ------------------------
# Task Attachment Inline
# ------------------------
class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = ("file_size", "uploaded_by", "created_at")


# ------------------------
# Checklist Inline
# ------------------------
class CheckListInline(admin.TabularInline):
    model = CheckList
    extra = 0


# ------------------------
# Task
# ------------------------
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "assigned_to",
        "status",
        "priority",
        "group",
        "created_at",
        "deadline",
    )

    list_filter = (
        "status",
        "priority",
        "is_routine",
        "created_at",
        "group",
    )

    search_fields = (
        "title",
        "description",
        "assigned_to__username",
        "group__title",
    )

    autocomplete_fields = (
        "assigned_to",
        "group",
        "status",
        "created_by",
        "parent_id",
        "root_task",
        "forwarded_by",
    )

    readonly_fields = ("created_at", "updated_at")

    inlines = [TaskAttachmentInline, CheckListInline]


# ------------------------
# Task Routine
# ------------------------
@admin.register(TaskRoutine)
class TaskRoutineAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "task",
        "period",
        "start_date",
        "next_run_at",
        "is_active",
    )

    list_filter = ("period", "is_active")

    search_fields = ("task__title",)


# ------------------------
# Task Attachment
# ------------------------
@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "file_name",
        "task",
        "uploaded_by",
        "file_size",
        "created_at",
    )

    search_fields = (
        "file_name",
        "task__title",
    )

    list_filter = ("file_type", "created_at")


# ------------------------
# Checklist
# ------------------------
@admin.register(CheckList)
class CheckListAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "task",
        "is_done",
        "created_at",
    )

    list_filter = ("is_done",)

    search_fields = ("title", "task__title")