from django.dispatch import receiver
from django.db.models.signals import post_save
from posts.models import Like, Comment
from .models import Notification


@receiver(post_save, sender=Like)
def notify_post_like(sender, instance, created, **kwargs):
    if created and instance.post.author != instance.user:
        Notification.objects.create(
            user=instance.post.author,
            actor=instance.user,
            verb=f"liked your post",
            target_url=f"/posts/{instance.post.id}/"
        )


@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created and instance.post.author != instance.author:
        Notification.objects.create(
            user=instance.post.author,
            actor=instance.author,
            verb=f"commented on your post",
            target_url=f"/posts/{instance.post.id}/"
        )
