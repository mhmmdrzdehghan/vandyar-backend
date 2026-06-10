from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

import json

from .models import (
    Message,
    Conversation,
    MessageReaction,
)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        print("CONNECTED:", self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):

        data = json.loads(text_data)

        event = data.get("event")

        if event == "message":
            await self.handle_message(data)

        elif event == "reaction":
            await self.handle_reaction(data)

    async def handle_message(self, data):

        message_text = data.get("message")

        user = self.scope["user"]

        if not user.is_authenticated:
            return

        if not message_text:
            return

        message = await self.save_message(
            user=user,
            message_text=message_text
        )

        await self.channel_layer.group_send(
        self.room_group_name,
        {
            "type": "chat_message",
            "event": "message",
            "message": message["content"],
            "message_id": message["id"],
            "groupid": message["group_id"],
            "user_id": user.id,
            "is_task": message["is_task"],
            "task_id": message["task_id"],
        }
    )

    async def handle_reaction(self, data):

        user = self.scope["user"]

        if not user.is_authenticated:
            return

        message_id = data.get("message_id")
        reaction = data.get("reaction")

        if not message_id or not reaction:
            return

        result = await self.save_reaction(
            user=user,
            message_id=message_id,
            reaction=reaction
        )

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

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "event": event["event"],
                    "message": event["message"],
                    "message_id": event["message_id"],
                    "groupid":event["groupid"],
                    "user_id": event["user_id"],
                    "is_task": event["is_task"],
                    "task_id": event["task_id"],
                }
            )
        )

    async def reaction_event(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "event": event["event"],
                    "message_id": event["message_id"],
                    "user_id": event["user_id"],
                    "reaction": event["reaction"],
                    "deleted": event["deleted"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, user, message_text):

        conversation = Conversation.objects.get(
            id=self.conversation_id
        )

        message = Message.objects.create(
        conversation=conversation,
        sender=user,
        content=message_text,
        is_task=False
    )

        return {
            "id": message.id,
            "content": message.content,
            "is_task": message.is_task,
            "task_id": message.task_id,
            "group_id": conversation.group_id,
        }

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

                return {
                    "deleted": True
                }

            existing.reaction = reaction
            existing.save()

            return {
                "deleted": False
            }

        MessageReaction.objects.create(
            message=message,
            user=user,
            reaction=reaction
        )

        return {
            "deleted": False
        }

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )