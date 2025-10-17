from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Post, Like, Comment, Repost
from django.contrib import messages
from django.views.decorators.http import require_POST

User = get_user_model()


@login_required
def feed_view(request):
    if request.method == "POST":
        text = request.POST.get("text")
        img = request.FILES.get("img")
        video = request.FILES.get("video")
        file = request.FILES.get("file")
        link = request.POST.get("link")

        if text or img or video or file or link:
            Post.objects.create(
                author=request.user,
                text=text,
                img=img,
                video=video,
                file=file,
                link=link
            )
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
        video = request.FILES.get("video")
        file = request.FILES.get("file")
        link = request.POST.get("link")

        if text or img or video or file or link:
            Post.objects.create(
                author=request.user,
                text=text,
                img=img,
                video=video,
                file=file,
                link=link
            )
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


@require_POST
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Коментар не може бути порожнім'}, status=400)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        text=text
    )

    # Аватар або стандартний
    if hasattr(request.user, 'profile') and request.user.profile.avatar:
        avatar_url = request.user.profile.avatar.url
    else:
        avatar_url = '/static/images/default-avatar.png'

    return JsonResponse({
        'comment_id': comment.id,
        'author': request.user.username,
        'text': comment.text,
        'avatar_url': avatar_url,
        'comment_count': post.comments.count(),
    })


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
    if request.user != post.author and not request.user.is_staff and not request.user.is_superuser:
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
    if request.user != comment.author and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Ви не маєте права видаляти цей коментар")
        return redirect("posts:feed")

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Коментар видалено")
        return redirect("posts:feed")

    return render(request, "posts/delete_comment.html", {"comment": comment})
@login_required
def repost_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Не дозволяємо репостити кілька разів
    if not Repost.objects.filter(user=request.user, original_post=post).exists():
        Repost.objects.create(user=request.user, original_post=post)
        messages.success(request, "Пост репостнуто!")
    else:
        messages.info(request, "Ви вже репостили цей пост.")
    return redirect("posts:feed")
