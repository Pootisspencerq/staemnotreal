from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Chat(models.Model):
    name = models.CharField(max_length=255, default="Глобальний чат")
    participants = models.ManyToManyField(User, related_name="chats", blank=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)  # фото замість вкладення
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message by {self.author} in {self.chat}"