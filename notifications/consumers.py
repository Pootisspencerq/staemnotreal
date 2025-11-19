# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user is None or user.is_anonymous:
            await self.close()
            return

        self.group_name = f"notifications_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        """
        Receives 'notify' events from group_send and forwards them to the client.
        Event format: {"type": "notify", "data": { ... }}
        """
        data = event.get("data", {})
        await self.send(text_data=json.dumps(data))

    async def receive(self, text_data=None, bytes_data=None):
        # Optionally respond to ping/pong
        if text_data:
            try:
                msg = json.loads(text_data)
            except Exception:
                return
            if msg.get("type") == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
