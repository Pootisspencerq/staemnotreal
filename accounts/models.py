from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    favorite_color = models.CharField(max_length=7, blank=True, null=True)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # 💬 Друзі
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def add_friend(self, profile):
        """Додає користувача до друзів (двосторонньо)"""
        if profile != self:
            self.friends.add(profile)
            profile.friends.add(self)

    def remove_friend(self, profile):
        """Видаляє дружбу"""
        if profile in self.friends.all():
            self.friends.remove(profile)
            profile.friends.remove(self)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Створює або оновлює профіль при створенні користувача"""
    if created:
        Profile.objects.create(user=instance)
    else:
        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.save()


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


class FriendRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    )

    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def accept(self):
        """Підтвердження дружби"""
        self.status = 'accepted'
        self.save()

        # додаємо двосторонню дружбу
        self.from_user.profile.add_friend(self.to_user.profile)

        # створюємо сповіщення, якщо модуль notifications існує
        try:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=self.from_user,
                sender=self.to_user,
                message=f"{self.to_user.username} прийняв(ла) твій запит у друзі.",
                notification_type="friend_accepted"
            )
        except ModuleNotFoundError:
            print("⚠️ notifications app not found — сповіщення не створено")

    def decline(self):
        """Відхиляє запит у друзі"""
        self.status = 'declined'
        self.save()

    def cancel(self):
        """Скасовує запит у друзі"""
        self.status = 'cancelled'
        self.save()

    def __str__(self):
        return f"FriendRequest(from={self.from_user}, to={self.to_user}, status={self.status})"
