from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification

User = settings.AUTH_USER_MODEL


def create_notification(recipient, verb, actor=None, description='', link=''):
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        description=description,
        link=link
    )


# --- CHAT MESSAGE NOTIFICATION ---
try:
    from chat.models import Message
except Exception:
    Message = None

if Message:
    @receiver(post_save, sender=Message)
    def notify_on_message(sender, instance, created, **kwargs):
        if not created:
            return

        # If your Message model has: sender, recipient
        if hasattr(instance, "recipient"):
            if instance.recipient != instance.sender:
                create_notification(
                    recipient=instance.recipient,
                    actor=instance.sender,
                    verb="sent you a message",
                    description=instance.text[:100] if hasattr(instance, "text") else '',
                    link=f"/chat/{instance.sender.id}/"
                )
