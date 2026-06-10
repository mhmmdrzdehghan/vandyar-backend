from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from .models import Message, Conversation
from account.models import User

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        print("CONNECTED:", self.room_group_name)

        print(dict(self.scope["headers"]))

        print(self.scope["user"])
        print(self.scope["user"].is_authenticated)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": "CONNECT TEST",
                "message_id": 0,
                "messag_istask": False,
                "message_task": None,
            }
        )

        
    async def receive(self, text_data):
        print("SENDING GROUP:", self.room_group_name)
        
        data = json.loads(text_data)

        message_text = data.get("message")
        user = self.scope["user"]

        

        message = await self.save_message(user, message_text)

        if not message:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "user_id": user.id,
                "message_id": message.id,
                "messag_istask": message.is_task,
                "message_task": message.task,
            }
        )

    async def chat_message(self, event):
        try:
            print("🔥 CHAT MESSAGE RECEIVED:", event)

            await self.send(text_data=json.dumps({
                "message": event.get("message"),
                "user_id": event.get("user_id"),
                "message_id": event.get("message_id"),
                "messag_istask": event.get("messag_istask"),
                "message_task": event.get("message_task"),
            }))

        except Exception as e:
            print("❌ CHAT MESSAGE ERROR:", e)

    @database_sync_to_async
    def save_message(self, user, message_text):
        conversation = Conversation.objects.get(id=self.conversation_id)

        return Message.objects.create(
            conversation=conversation,
            sender_id=user.id,
            content=message_text,
            is_task=False
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )