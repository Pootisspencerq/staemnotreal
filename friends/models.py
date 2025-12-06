from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    to_user   = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user} → {self.to_user}"


class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name="friends_main", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="friends_secondary", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"

    @staticmethod
    def get_friends(user):
        friends1 = Friendship.objects.filter(user1=user).values_list("user2", flat=True)
        friends2 = Friendship.objects.filter(user2=user).values_list("user1", flat=True)
        return User.objects.filter(id__in=friends1.union(friends2))
