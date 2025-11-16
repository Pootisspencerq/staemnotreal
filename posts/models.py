from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Group(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='groups/covers/', blank=True, null=True)

    def __str__(self):
        return self.name


class ChatThread(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chat_threads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Chat #{self.pk}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField(null=True, blank=True)

    img = models.ImageField(upload_to='posts/images/', null=True, blank=True)
    video = models.FileField(upload_to='posts/videos/', null=True, blank=True)
    file = models.FileField(upload_to='posts/files/', null=True, blank=True)
    link = models.URLField(null=True, blank=True)

    # main repost mechanism
    shared_from = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='shares'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # context
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    chat_thread = models.ForeignKey(ChatThread, null=True, blank=True, on_delete=models.CASCADE, related_name='messages')
    is_chat_message = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        preview = (self.text[:30] + "...") if self.text else "(no text)"
        return f"{self.author}: {preview}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def repost_count(self):
        return self.shares.count()


class PostMedia(models.Model):
    MEDIA_IMAGE = 'image'
    MEDIA_VIDEO = 'video'
    MEDIA_FILE = 'file'
    MEDIA_LINK = 'link'

    MEDIA_TYPES = [
        (MEDIA_IMAGE, 'Image'),
        (MEDIA_VIDEO, 'Video'),
        (MEDIA_FILE, 'File'),
        (MEDIA_LINK, 'Link'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)

    image = models.ImageField(upload_to='posts/media/images/', blank=True, null=True)
    file = models.FileField(upload_to='posts/media/files/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Media({self.media_type}) for Post {self.post_id}"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/gallery/')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for Post {self.post_id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} liked post {self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on Post {self.post.id}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    vote_value = models.IntegerField()  # 1 (upvote) or -1 (downvote)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} voted {self.vote_value} on post {self.post.id}"
