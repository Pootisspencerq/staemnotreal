from django.conf import settings
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from .models import Notification

User = settings.AUTH_USER_MODEL

# ---- Customize these imports to match your project structure ----
# Example import statements — change to your app.module names if different:
try:
    from tasks.models import Task  # app: tasks
except Exception:
    Task = None

try:
    from chat.models import Message  # app: chat
except Exception:
    Message = None

try:
    from workshops.models import Workshop, WorkshopMembership
except Exception:
    Workshop = None
    WorkshopMembership = None
# -----------------------------------------------------------------

def create_notification(recipient, verb, actor=None, target=None, link='', description='', data=None):
    data = data or {}
    ct = None
    oid = None
    if target is not None:
        ct = ContentType.objects.get_for_model(target.__class__)
        oid = getattr(target, 'pk', None)
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        description=description,
        content_type=ct,
        object_id=str(oid) if oid is not None else None,
        link=link or '',
        data=data
    )

# Example: New Task created -> notify the project members, or owner follower(s)
if Task:
    @receiver(post_save, sender=Task)
    def notify_on_task_create(sender, instance, created, **kwargs):
        if not created:
            return
        # decide recipients — here: assigned users or project members
        recipients = []
        # if Task has `assigned_to` FK or M2M use it; otherwise notify the creator followers (customize)
        assigned = getattr(instance, 'assigned_to', None)
        if assigned is None:
            # fallback: notify the creator's followers or everyone (customize)
            pass
        else:
            # support both FK and M2M-like attributes
            if hasattr(instance.__class__, 'assigned_to') and hasattr(instance.assigned_to, 'all'):
                recipients = list(instance.assigned_to.all())
            elif assigned:
                recipients = [assigned]
        # avoid notifying the author themselves if present
        actor = getattr(instance, 'created_by', None) or getattr(instance, 'author', None)
        for r in recipients:
            if not r or (actor and r == actor):
                continue
            link = getattr(instance, 'get_absolute_url', lambda: '#')()
            create_notification(recipient=r,
                                verb='created a task' if actor else 'New task',
                                actor=actor,
                                target=instance,
                                link=link,
                                description=f"Task: {getattr(instance, 'title', str(instance))}")

# Example: New chat message -> notify the chat recipient(s)
if Message:
    @receiver(post_save, sender=Message)
    def notify_on_message(sender, instance, created, **kwargs):
        if not created:
            return
        # Message should define chat or recipients — customize to your Message model
        # Common patterns: Message has `chat` with participants; or `recipient` field
        recipients = []
        if hasattr(instance, 'recipient') and instance.recipient:
            recipients = [instance.recipient]
        elif hasattr(instance, 'chat') and instance.chat:
            # assume chat.participants exists
            participants = getattr(instance.chat, 'participants', None)
            if participants is not None:
                recipients = [u for u in participants.all() if u != instance.author]
        # create notifications
        for r in recipients:
            create_notification(
                recipient=r,
                verb='sent you a message',
                actor=instance.author if hasattr(instance, 'author') else None,
                target=instance,
                link=getattr(instance, 'get_absolute_url', lambda: '#')(),
                description=(instance.text[:150] if hasattr(instance, 'text') else '')
            )

# Example: Workshop membership added -> notify the invited user
if WorkshopMembership:
    @receiver(post_save, sender=WorkshopMembership)
    def notify_on_workshop_join(sender, instance, created, **kwargs):
        if not created:
            return
        # Assuming WorkshopMembership has fields: user, workshop, added_by
        user = getattr(instance, 'user', None)
        workshop = getattr(instance, 'workshop', None)
        added_by = getattr(instance, 'added_by', None)
        if not user or not workshop:
            return
        create_notification(
            recipient=user,
            verb='added you to a workshop',
            actor=added_by,
            target=workshop,
            link=getattr(workshop, 'get_absolute_url', lambda: '#')(),
            description=f"You were added to workshop {getattr(workshop, 'title', str(workshop))}"
        )
