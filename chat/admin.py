from django.contrib import admin
from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "name")  # видалити created_at
    # ordering = ("created_at",)   # видалити або замінити на "id"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "author", "text", "created_at")
    ordering = ("created_at",)