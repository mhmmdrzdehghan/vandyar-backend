from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("CONECTED VOTIFICATION ")


        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        self.group_name = f"notification_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):

        print("NOTIFICATION RECEIVED :", event)


        await self.send(
            text_data=json.dumps(
                    {
                        "event": "notification",
                        "id": event.get("id"),
                        "title": event["title"],
                        "message": event["message"],
                        "created_at": event.get("created_at"),
                    }
            )
        )

 