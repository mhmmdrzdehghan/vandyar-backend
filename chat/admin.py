from django.contrib import admin
from .models import (
    Conversation,
    ConversationMember,
    Message,
    MessageReaction
)


class ConversationMemberInline(admin.TabularInline):
    model = ConversationMember
    extra = 0
    autocomplete_fields = ["user"]
    readonly_fields = ["created_at", "updated_at"]


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["created_at", "updated_at"]
    fields = ["sender", "content", "is_task", "task", "created_at"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "title", "created_by", "created_at"]
    list_filter = ["type", "created_at"]
    search_fields = ["title", "created_by__username"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ConversationMemberInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "created_by",
            "group",
            "task"
        )


@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
    list_display = (
        "conversation",
        "user",
        "is_admin",
        "last_read_message",
        "created_at",
    )

    list_filter = (
        "is_admin",
        "conversation",
    )

    search_fields = (
        "user__username",
        "user__email",
        "conversation__title",
    )

    autocomplete_fields = (
        "conversation",
        "user",
        "last_read_message",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "conversation",
        "user",
        "last_read_message",
    )



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "conversation", "sender", "is_task", "created_at"]
    list_filter = ["is_task", "created_at"]
    search_fields = ["content", "sender__username"]
    autocomplete_fields = ["conversation", "sender", "task"]
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "conversation",
            "sender",
            "task"
        )


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ["message", "user", "reaction", "created_at"]
    list_filter = ["reaction", "created_at"]
    search_fields = ["user__username", "message__content"]
    autocomplete_fields = ["message", "user"]
    readonly_fields = ["created_at"]