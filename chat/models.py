from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# -------------------
# 🔹 Модель Chat
# -------------------
class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        return f"Chat {self.id}"

# -------------------
# 🔹 Модель Message
# -------------------
class Message(models.Model):
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        null=True,       # дозволяємо null
        blank=True
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_messages',
        on_delete=models.CASCADE,
        null=True,       # дозволяємо null
        blank=True
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.text[:20]}"