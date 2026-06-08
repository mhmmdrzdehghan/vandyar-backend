from django.contrib import admin
from .models import Task, Status, TaskRoutine, TaskAttachment, CheckList


# ----------------------
# STATUS
# ----------------------
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)
    ordering = ("id",)


# ----------------------
# CHECKLIST INLINE
# ----------------------
class CheckListInline(admin.TabularInline):
    model = CheckList
    extra = 0
    fields = ("title", "is_done", "created_at")
    readonly_fields = ("created_at",)


# ----------------------
# ATTACHMENT INLINE
# ----------------------
class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = ("file_size", "file_type", "uploaded_by", "created_at")


# ----------------------
# TASK ROUTINE INLINE
# ----------------------
class TaskRoutineInline(admin.StackedInline):
    model = TaskRoutine
    can_delete = False


# ----------------------
# TASK ADMIN
# ----------------------
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "assigned_to",
        "group",
        "deadline",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "is_routine",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "assigned_to__username",
        "created_by__username",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")

    inlines = [
        CheckListInline,
        TaskAttachmentInline,
        TaskRoutineInline,
    ]

    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "description", "group", "status", "priority")
        }),
        ("Assignment", {
            "fields": ("assigned_to", "created_by", "can_forward")
        }),
        ("Timeline", {
            "fields": ("planned_start_at", "deadline", "start_time", "end_time")
        }),
        ("Extra", {
            "fields": ("parent_id", "root_task", "quality_rate", "is_routine")
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at")
        }),
    )


# ----------------------
# ATTACHMENT ADMIN (standalone)
# ----------------------
@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "task", "uploaded_by", "file_size", "created_at")
    search_fields = ("file_name", "task__title")
    list_filter = ("created_at",)


# ----------------------
# CHECKLIST ADMIN
# ----------------------
@admin.register(CheckList)
class CheckListAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "task", "is_done", "created_at")
    list_filter = ("is_done",)
    search_fields = ("title", "task__title")


# ----------------------
# TASK ROUTINE ADMIN
# ----------------------
@admin.register(TaskRoutine)
class TaskRoutineAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "period", "next_run_at", "is_active")
    list_filter = ("period", "is_active")
    search_fields = ("task__title",)