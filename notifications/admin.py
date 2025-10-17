from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'verb', 'unread', 'created_at')
    list_filter = ('unread',)
    search_fields = ('verb', 'user__username', 'actor__username')
    ordering = ('-created_at',)
