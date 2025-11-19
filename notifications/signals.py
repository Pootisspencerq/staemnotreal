# notifications/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification
from .utils import create_notification  # use the helper that also broadcasts

User = settings.AUTH_USER_MODEL

# Backwards-compatible direct-create helper kept for callers if needed
def create_notification_fallback(recipient, verb, actor=None, description='', link=''):
    return create_notification(recipient, verb, actor=actor, description=description, link=link)


# Chat message notifications (if chat app present)
try:
    from chat.models import Message
except Exception:
    Message = None

if Message:
    @receiver(post_save, sender=Message)
    def notify_on_message(sender, instance, created, **kwargs):
        if not created:
            return

        if hasattr(instance, "recipient") and instance.recipient and instance.sender != instance.recipient:
            create_notification(
                recipient=instance.recipient,
                actor=instance.sender,
                verb="sent you a message",
                description=getattr(instance, "text", "")[:200],
                link=f"/chat/{instance.sender.id}/"
            )
