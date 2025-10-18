from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    """
    In-app notification model.
    - recipient: who receives it
    - actor: optional user who triggered the notification
    - verb: short text like "created", "commented", "invited"
    - target_content_type / target_object_id: generic relation to the object (Task, Message, etc.)
    - unread: boolean
    - data: optional JSON for extra fields (link, preview text)
    """
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    actor = models.ForeignKey(User, related_name='actor_notifications', null=True, blank=True, on_delete=models.SET_NULL)
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # optional human readable text
    timestamp = models.DateTimeField(default=timezone.now)
    unread = models.BooleanField(default=True)
    # generic relation to the object that caused the notification
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    # auxiliary link to redirect the user - stored as relative URL
    link = models.CharField(max_length=1024, blank=True)
    # small JSON store if needed for extra metadata
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['recipient', 'unread']),
        ]

    def __str__(self):
        return f"Notification(to={self.recipient}, verb={self.verb}, unread={self.unread})"

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save(update_fields=['unread'])

    def get_absolute_url(self):
        if self.link:
            return self.link
        # fallback: no link
        return '#'
