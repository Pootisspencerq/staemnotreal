from django.contrib import admin
from .models import Group, Membership


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "group", "joined_at")
    list_filter = ("group", "user")
    ordering = ("-joined_at",)
