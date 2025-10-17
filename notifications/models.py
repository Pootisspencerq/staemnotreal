from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    user = models.ForeignKey(
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
    verb = models.CharField(max_length=255)  # "liked your post", "commented"
    target_url = models.URLField(blank=True, null=True)  # optional link
    unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor} {self.verb} → {self.user}"

    def mark_as_read(self):
        self.unread = False
        self.save()
