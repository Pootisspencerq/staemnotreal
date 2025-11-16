from django.contrib import admin
from .models import Profile
from posts.models import Post

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "favorite_color", "total_posts", "total_reposts")
    search_fields = ("user__username", "bio")
    list_filter = ("favorite_color", "role")

    # Total number of posts by the user (including original posts and reposts)
    def total_posts(self, obj):
        return obj.user.posts.count()
    total_posts.short_description = "Posts"

    # Total number of reposts made by the user's posts
    def total_reposts(self, obj):
        # Sum of shares for all posts authored by the user
        return sum(post.shares.count() for post in obj.user.posts.all())
    total_reposts.short_description = "Reposts"
