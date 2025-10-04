from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_text', 'created_at')

    def short_text(self, obj):
        return (obj.text[:30] + '...') if obj.text else '(no text)'
    short_text.short_description = 'Text'

    search_fields = ("title", "content")
    list_filter = ("author", "created_at")
    ordering = ("-created_at",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    search_fields = ("content",)
    list_filter = ("author", "created_at")
    ordering = ("-created_at",)
