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

    # ⚠️ MUST be string reference
    participants = models.ManyToManyField(
        User,
        related_name='chat_threads',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Chat #{self.pk}"


class Post(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )

    text = models.TextField(blank=True, null=True)

    # legacy single-media (optional, can be removed later)
    img = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    file = models.FileField(upload_to='posts/files/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    # repost
    shared_from = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='shares'
    )

    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    chat_thread = models.ForeignKey(
        ChatThread,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    is_chat_message = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        preview = (self.text[:30] + '...') if self.text else '(no text)'
        return f'{self.author}: {preview}'

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

    MEDIA_TYPES = (
        (MEDIA_IMAGE, 'Image'),
        (MEDIA_VIDEO, 'Video'),
        (MEDIA_FILE, 'File'),
        (MEDIA_LINK, 'Link'),
    )

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='media'
    )

    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)

    image = models.ImageField(upload_to='posts/media/images/', blank=True, null=True)
    file = models.FileField(upload_to='posts/media/files/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(media_type='image', image__isnull=False) |
                    models.Q(media_type='video', file__isnull=False) |
                    models.Q(media_type='file', file__isnull=False) |
                    models.Q(media_type='link', url__isnull=False)
                ),
                name='postmedia_valid_content'
            )
        ]

    def __str__(self):
        return f'Media({self.media_type}) for Post {self.post_id}'


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [models.Index(fields=['post'])]

    def __str__(self):
        return f'{self.user} liked post {self.post.id}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on Post {self.post.id}'


class Vote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1

    VOTE_CHOICES = (
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='votes'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='votes'
    )
    vote_value = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user} voted {self.vote_value} on post {self.post.id}'
