from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Post, Like, Comment
from accounts.models import Follow
from django.contrib import messages
from django.views.decorators.http import require_POST
User = get_user_model()


@login_required
def feed_view(request):
    if request.method == "POST":
        text = request.POST.get("text")
        img = request.FILES.get("img")  # 🟢 беремо файл
        if text or img:  # дозволяємо пости тільки з текстом, тільки з картинкою або обидва
            Post.objects.create(author=request.user, text=text, img=img)
        return redirect("posts:feed")

    posts = Post.objects.all().select_related("author").prefetch_related("comments", "likes")
    for post in posts:
        post.liked_by_user = (
            request.user.is_authenticated
            and post.likes.filter(user=request.user).exists()
        )
    return render(request, "posts/feed.html", {"posts": posts})


@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        img = request.FILES.get("img")  # 🟢 беремо файл
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


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get("text")
    if text:
        comment = Comment.objects.create(post=post, author=request.user, text=text)
        return JsonResponse({
            "author": comment.author.username,
            "text": comment.text,
            "comment_count": post.comments.count(),
        })
    return JsonResponse({"error": "empty"}, status=400)

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
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост видалено")
        return redirect("posts:feed")
    return render(request, "posts/delete_post.html", {"post": post})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Коментар видалено")
    return redirect("posts:feed")
