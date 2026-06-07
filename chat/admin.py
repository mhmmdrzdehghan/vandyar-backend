from django.contrib import admin

from .models import (
    Conversation,
    ConversationMember,
    Message
)


class ConversationMemberInline(admin.TabularInline):
    model = ConversationMember
    extra = 0
    autocomplete_fields = ["user"]


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = [
        "sender",
        "content",
        "created_at"
    ]
    ordering = ["-created_at"]
    show_change_link = True


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "type",
        "group",
        "created_by",
        "members_count",
        "created_at",
    )

    list_filter = (
        "type",
        "created_at",
    )

    search_fields = (
        "title",
        "created_by__email",
        "group__title",
    )

    autocomplete_fields = (
        "created_by",
        "group",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (
        ConversationMemberInline,
        MessageInline,
    )

    def members_count(self, obj):
        return obj.members.count()

    members_count.short_description = "Members"


@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "user",
        "is_admin",
        "created_at",
    )

    list_filter = (
        "is_admin",
        "created_at",
    )

    search_fields = (
        "user__email",
        "conversation__title",
    )

    autocomplete_fields = (
        "conversation",
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "conversation",
        "sender",
        "short_content",
        "is_task",
        "created_at",
    )

    list_filter = (
        "is_task",
        "created_at",
    )

    search_fields = (
        "content",
        "sender__email",
        "conversation__title",
    )

    autocomplete_fields = (
        "conversation",
        "sender",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    def short_content(self, obj):
        return obj.content[:50]

    short_content.short_description = "Message"