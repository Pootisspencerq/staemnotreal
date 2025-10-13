from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Створює профіль при реєстрації користувача
    або перевіряє наявність існуючого профілю.
    """
    # Створюємо тільки якщо профілю немає
    Profile.objects.get_or_create(user=instance)
