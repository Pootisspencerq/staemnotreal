from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "favorite_color")
    search_fields = ("user__username", "bio")
    list_filter = ("favorite_color",)


