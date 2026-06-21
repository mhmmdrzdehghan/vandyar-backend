from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

import json

from .models import (
    Message,
    Conversation,
    MessageReaction,
)



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"
        self.user_group_name = f"user_{self.user.id}"

        # گروه چت
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # گروه شخصی کاربر برای unread
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    # -----------------------------
    # RECEIVE
    # -----------------------------
    async def receive(self, text_data):

        data = json.loads(text_data)
        event = data.get("event")

        if event == "message":
            await self.handle_message(data)

        elif event == "reaction":
            await self.handle_reaction(data)

        elif event == "edit":
            await self.handle_edit(data)

        elif event == "delete":
            await self.handle_delete(data)

        elif event == "read":
            await self.mark_as_read()

    # -----------------------------
    # DB: unread count
    # -----------------------------

    @database_sync_to_async
    def get_unread_count(self, conversation_id, user_id):

        from chat.models import ConversationMember, Message

        member = ConversationMember.objects.select_related(
            "last_read_message"
        ).get(
            conversation_id=conversation_id,
            user_id=user_id
        )

        if member.last_read_message_id:
            return Message.objects.filter(
                conversation_id=conversation_id,
                id__gt=member.last_read_message_id
            ).exclude(sender_id=user_id).count()

        return Message.objects.filter(
            conversation_id=conversation_id
        ).exclude(sender_id=user_id).count()

    # -----------------------------
    # DB: members
    # -----------------------------

    @database_sync_to_async
    def get_conversation_members(self, conversation_id):

        from chat.models import ConversationMember

        return list(
            ConversationMember.objects.filter(
                conversation_id=conversation_id
            ).values_list("user_id", flat=True)
        )

    # -----------------------------
    # DB: mark read
    # -----------------------------

    @database_sync_to_async
    def mark_read_db(self):

        from chat.models import ConversationMember, Message

        last_message = Message.objects.filter(
            conversation_id=self.conversation_id
        ).order_by("-id").first()

        if not last_message:
            return

        ConversationMember.objects.filter(
            conversation_id=self.conversation_id,
            user_id=self.user.id
        ).update(last_read_message=last_message)

    # -----------------------------
    # MESSAGE
    # -----------------------------

    async def handle_message(self, data):

        user = self.user

        content = data.get("message")
        reply_to = data.get("reply_to")

        if not content:
            return

        message = await self.save_message(user, content, reply_to)

        # ارسال پیام به چت
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "event": "message",
                "message_id": message["id"],
                "message": message["content"],
                "reply_to": message["reply_to"],
                "user_id": user.id,
            }
        )

        # گرفتن اعضای چت
        members = await self.get_conversation_members(self.conversation_id)

        # ارسال unread به هر کاربر
        for member_id in members:

            if member_id == user.id:
                continue

            unread = await self.get_unread_count(
                self.conversation_id,
                member_id
            )

            await self.channel_layer.group_send(
                f"user_{member_id}",
                {
                    "type": "unread_update",
                    "conversation_id": self.conversation_id,
                    "unread": unread,
                }
            )

    # -----------------------------
    # MARK AS READ
    # -----------------------------

    async def mark_as_read(self):

        await self.mark_read_db()

        await self.channel_layer.group_send(
            f"user_{self.user.id}",
            {
                "type": "unread_update",
                "conversation_id": self.conversation_id,
                "unread": 0,
            }
        )

    # -----------------------------
    # SEND EVENTS
    # -----------------------------

    async def chat_message(self, event):

        await self.send(text_data=json.dumps(event))

    async def unread_update(self, event):

        await self.send(text_data=json.dumps({
            "event": "unread",
            "conversation_id": event["conversation_id"],
            "unread": event["unread"],
        }))


    # -----------------------------
    # REACTION
    # -----------------------------
    async def handle_reaction(self, data):

        user = self.scope["user"]
        if not user.is_authenticated:
            return

        message_id = data.get("message_id")
        reaction = data.get("reaction")

        if not message_id or not reaction:
            return

        result = await self.save_reaction(user, message_id, reaction)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "reaction_event",
                "event": "reaction",
                "message_id": message_id,
                "user_id": user.id,
                "reaction": reaction,
                "deleted": result["deleted"],
            }
        )

    # -----------------------------
    # EDIT MESSAGE
    # -----------------------------
    async def handle_edit(self, data):

        user = self.scope["user"]
        if not user.is_authenticated:
            return

        message_id = data.get("message_id")
        new_content = data.get("message")

        if not message_id or not new_content:
            return

        message = await self.edit_message(user, message_id, new_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_edited",
                "event": "edit",
                "message_id": message_id,
                "message": message["content"],
                "user_id": user.id,
                "is_task": message["is_task"],
                "task_id": message["task_id"],
            }
        )

    # -----------------------------
    # DELETE MESSAGE (SOFT DELETE)
    # -----------------------------
    async def handle_delete(self, data):

        user = self.scope["user"]
        if not user.is_authenticated:
            return

        message_id = data.get("message_id")

        if not message_id:
            return

        await self.delete_message(user, message_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_deleted",
                "event": "delete",
                "message_id": message_id,
                "user_id": user.id,
            }
        )

    # -----------------------------
    # GROUP EVENTS
    # -----------------------------
    async def chat_message(self, event):

        await self.send(text_data=json.dumps(event))

    async def reaction_event(self, event):

        await self.send(text_data=json.dumps(event))

    async def message_edited(self, event):

        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):

        await self.send(text_data=json.dumps(event))

    # -----------------------------
    # DB OPERATIONS
    # -----------------------------
    @database_sync_to_async
    def save_message(self, user, content, reply_to=None):

        conversation = Conversation.objects.get(id=self.conversation_id)

        reply_message = None
        if reply_to:
            reply_message = Message.objects.filter(id=reply_to).first()

        # 1. پیام اصلی
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content,
            is_task=False,
            reply_to=reply_message
        )

        # 2. اگر reply روی task بود → پیام در task chat هم ساخته شود
        if reply_message and reply_message.is_task and reply_message.task:

            task_conversation = Conversation.objects.filter(
                task=reply_message.task
            ).first()

            if task_conversation:

                Message.objects.create(
                    conversation=task_conversation,
                    sender=user,
                    content=f"[Reply] {content}",
                    is_task=False,
                    reply_to=reply_message
                )

        return {
            "id": message.id,
            "content": message.content,
            "is_task": message.is_task,
            "task_id": message.task_id,
            "reply_to": message.reply_to.id if message.reply_to else None
        }

    # -----------------------------
    # REACTION
    # -----------------------------
    @database_sync_to_async
    def save_reaction(self, user, message_id, reaction):

        message = Message.objects.get(id=message_id)

        existing = MessageReaction.objects.filter(
            message=message,
            user=user
        ).first()

        if existing:

            if existing.reaction == reaction:
                existing.delete()
                return {"deleted": True}

            existing.reaction = reaction
            existing.save()
            return {"deleted": False}

        MessageReaction.objects.create(
            message=message,
            user=user,
            reaction=reaction
        )

        return {"deleted": False}

    # -----------------------------
    # EDIT (NEW MODEL SUPPORTED)
    # -----------------------------
    @database_sync_to_async
    def edit_message(self, user, message_id, new_content):

        message = Message.objects.get(id=message_id)

        if message.sender_id != user.id:
            return {
            "id": message.id,
            "content": message.content,
            "is_task": message.is_task,
            "task_id": message.task_id,
        }

        message.content = new_content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()

        return {
            "id": message.id,
            "content": message.content,
            "is_task": message.is_task,
            "task_id": message.task_id,
        }

    # -----------------------------
    # DELETE (SOFT DELETE)
    # -----------------------------
    @database_sync_to_async
    def delete_message(self, user, message_id):

        message = Message.objects.get(id=message_id)

        if message.sender_id != user.id:
            return False

        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()

        return True

    # -----------------------------
    # DISCONNECT
    # -----------------------------
    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )