from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Створює профіль при реєстрації користувача
    або оновлює існуючий профіль.
    """
    # Створення нового профілю, якщо його немає
    profile, _ = Profile.objects.get_or_create(user=instance)

    # Оновлення профілю
    profile.save()
@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=instance)
    profile.save()