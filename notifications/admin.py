from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'verb', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('verb', 'description', 'recipient__username', 'actor__username')
    readonly_fields = ('timestamp',)
