# notifications/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Notification

def create_notification(recipient, verb, actor=None, description='', link=''):
    """
    Create a Notification instance and broadcast it to the recipient's notification group
    so connected websocket clients receive it immediately.
    Returns the created Notification instance.
    """
    n = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        description=description,
        link=link,
        timestamp=timezone.now(),
        is_read=False
    )

    # Prepare payload
    data = {
        "id": n.id,
        "verb": n.verb,
        "description": n.description,
        "link": n.link or "#",
        "timestamp": n.timestamp.isoformat(),
        "is_read": n.is_read,
        "actor": getattr(n.actor, "username", None),
        "recipient_id": recipient.id,
    }

    # Send via channel layer to the recipient group
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"notifications_{recipient.id}",
            {"type": "notify", "data": data}
        )

    return n
