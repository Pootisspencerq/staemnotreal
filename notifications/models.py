from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_from'
    )
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # NEW FIELD
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient} - {self.verb}"

