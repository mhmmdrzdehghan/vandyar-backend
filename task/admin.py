from django.contrib import admin
from .models import (
    Task,
    TaskRoutine,
    TaskAttachment,
    CheckList,
    Status
)


# =========================
# STATUS
# =========================
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)


# =========================
# CHECKLIST INLINE
# =========================
class CheckListInline(admin.TabularInline):
    model = CheckList
    extra = 0
    fields = ("title", "is_done")
    show_change_link = True


# =========================
# ATTACHMENT INLINE
# =========================
class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = ("file_name", "file_size", "file_type", "uploaded_by")
    show_change_link = True


# =========================
# TASK ROUTINE INLINE
# =========================
class TaskRoutineInline(admin.StackedInline):
    model = TaskRoutine
    extra = 0


# =========================
# TASK ADMIN
# =========================
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "subproject",
        "status",
        "priority",
        "assigned_to",
        "can_forward",
        "created_by",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "is_routine",
        "can_forward",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "assigned_to__email",
        "created_by__email",
    )

    autocomplete_fields = (
        "subproject",
        "assigned_to",
        "status",
        "created_by",
        "parent_id",
        "root_task",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (
        CheckListInline,
        TaskAttachmentInline,
        TaskRoutineInline,
    )


# =========================
# TASK ROUTINE ADMIN
# =========================
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


# =========================
# ATTACHMENT ADMIN
# =========================
@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "task",
        "file_name",
        "file_size",
        "file_type",
        "uploaded_by",
        "created_at",
    )

    search_fields = (
        "file_name",
        "task__title",
    )

    autocomplete_fields = (
        "task",
        "uploaded_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# =========================
# CHECKLIST ADMIN
# =========================
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
    )

    search_fields = (
        "title",
        "task__title",
    )

    autocomplete_fields = (
        "task",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )