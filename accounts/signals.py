from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.apps import apps

from .models import Profile, FriendRequest


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Створює профіль при реєстрації користувача
    або перевіряє наявність існуючого профілю.
    """
    Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=FriendRequest)
def friend_request_notification(sender, instance, created, **kwargs):
    """
    Створює сповіщення при надсиланні або прийнятті запиту в друзі.
    """
    Notification = apps.get_model('notifications', 'Notification')

    if not Notification:
        # Якщо додаток notifications відсутній
        return

    # 📨 Коли створено новий запит у друзі
    if created and instance.status == 'pending':
        Notification.objects.create(
            user=instance.to_user,                # Кому показати сповіщення
            actor=instance.from_user,             # Хто виконав дію
            verb='надіслав(ла) запит у друзі',
            data={
                'type': 'friend_request',
                'from_user_id': instance.from_user.id
            }
        )

    # ✅ Коли запит прийнято
    elif instance.status == 'accepted':
        Notification.objects.create(
            user=instance.from_user,
            actor=instance.to_user,
            verb='прийняв(ла) твій запит у друзі',
            data={
                'type': 'friend_request_accepted',
                'to_user_id': instance.to_user.id
            }
        )
