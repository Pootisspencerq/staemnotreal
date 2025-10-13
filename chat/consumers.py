import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.chat_id}"

        # Перевірка: користувач має бути аутентифікований і учасником чату
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        is_participant = await database_sync_to_async(self._is_participant)(user, self.chat_id)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    def _is_participant(self, user, chat_id):
        try:
            chat = Chat.objects.get(pk=chat_id)
            return chat.participants.filter(pk=user.pk).exists()
        except Chat.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        data = json.loads(text_data)
        message_text = data.get("message", "").strip()

        user = self.scope["user"]
        if not user.is_authenticated:
            return

        # збереження повідомлення в БД
        message_obj = await database_sync_to_async(self._create_message)(user, self.chat_id, message_text)

        payload = {
            "id": message_obj.id,
            "chat_id": self.chat_id,
            "author_id": user.id,
            "author_username": user.get_username(),
            "message": message_obj.content,
            "attachment_url": message_obj.attachment.url if message_obj.attachment else None,
            "created_at": message_obj.created_at.isoformat(),
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "payload": payload
            }
        )

    def _create_message(self, user, chat_id, content):
        chat = Chat.objects.get(pk=chat_id)
        return Message.objects.create(chat=chat, author=user, content=content)

    async def chat_message(self, event):
        payload = event["payload"]
        await self.send(text_data=json.dumps(payload))
