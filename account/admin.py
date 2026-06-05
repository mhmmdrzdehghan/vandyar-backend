from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "role",
        "is_staff",
        "is_active",
        "created_at",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")

    inlines = [ProfileInline]

    fieldsets = (
        ("اطلاعات کاربر", {
            "fields": ("username", "password")
        }),
        ("سطح دسترسی", {
            "fields": ("role", "is_staff", "is_active", "is_superuser", "groups", "user_permissions")
        }),
        ("تاریخ‌ها", {
            "fields": ("created_at", "updated_at")
        }),
    )

    add_fieldsets = (
        ("ساخت کاربر", {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "phone",
        "first_name",
        "last_name",
        "created_at",
    )

    search_fields = (
        "phone",
        "first_name",
        "last_name",
        "user__username",
    )

    list_filter = ("created_at",)

    readonly_fields = ("created_at", "updated_at")
