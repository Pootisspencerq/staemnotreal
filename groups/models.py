from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')  # ✅ додано поле
    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_moderator = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        role = " (модератор)" if self.is_moderator else ""
        return f"{self.user.username} у {self.group.name}{role}"


class GroupPost(models.Model):
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to="group_files/", blank=True, null=True)  # ✅ будь-який файл
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Пост від {self.author.username} у {self.group.name}"
