from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from posts.models import Post

@login_required
def home_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-timestamp')[:10]

    posts = Post.objects.filter(is_public=True).select_related('author')

    return render(request, 'home.html', {
        'notifications': notifications,
        'posts': posts,
    })