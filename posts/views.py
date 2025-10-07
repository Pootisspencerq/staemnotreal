from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Post, Like, Comment
from django.contrib import messages
from django.views.decorators.http import require_POST

User = get_user_model()


@login_required
def feed_view(request):
    if request.method == "POST":
        text = request.POST.get("text")
        img = request.FILES.get("img")
        if text or img:
            Post.objects.create(author=request.user, text=text, img=img)
        return redirect("posts:feed")

    posts = Post.objects.all().select_related("author").prefetch_related("comments", "likes")
    for post in posts:
        post.liked_by_user = request.user.is_authenticated and post.likes.filter(user=request.user).exists()
    return render(request, "posts/feed.html", {"posts": posts})


@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        img = request.FILES.get("img")
        if text or img:
            Post.objects.create(author=request.user, text=text, img=img)
        return redirect("posts:feed")
    return redirect("posts:feed")


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True

    return JsonResponse({
        "liked": liked,
        "like_count": post.likes.count(),
    })


def add_comment(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get('text', '').strip()
        if text:
            comment = Comment.objects.create(post=post, author=request.user, text=text)
            comment_count = post.comments.count()
            avatar_url = '/static/images/default-avatar.png'
            if hasattr(comment.author, 'profile') and comment.author.profile.avatar:
                avatar_url = comment.author.profile.avatar.url
            return JsonResponse({
                'comment_id': comment.id,
                'text': comment.text,
                'author': comment.author.username,
                'avatar_url': avatar_url,
                'comment_count': comment_count
            })
    return JsonResponse({'error': 'Не вдалося додати коментар'}, status=400)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            post.text = text
            post.save()
            messages.success(request, "Пост оновлено")
            return redirect("posts:feed")
    return render(request, "posts/edit_post.html", {"post": post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Ви не маєте права видаляти цей пост")
        return redirect("posts:feed")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост видалено")
        return redirect("posts:feed")

    return render(request, "posts/delete_post.html", {"post": post})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('posts:feed')
    return render(request, 'posts/delete_comment.html', {'comment': comment})