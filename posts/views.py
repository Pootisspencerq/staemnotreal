from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Post, Like, Comment
from accounts.models import Follow
from django.contrib import messages
User = get_user_model()


@login_required
def feed_view(request):
    following_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)

    posts = (
        Post.objects.select_related("author")
        .prefetch_related("comments", "likes")
        .filter(author__in=list(following_ids) + [request.user.id])
        .order_by("-created_at")
    )

    # Add liked_by_user attribute for template
    for post in posts:
        post.liked_by_user = post.likes.filter(user=request.user).exists()

    return render(request, "posts/feed.html", {"posts": posts})



@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Post.objects.create(author=request.user, text=text)
        return redirect("posts:feed")
    return redirect("posts:feed")


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()   # якщо вже лайкнув → забрати
    else:
        Like.objects.create(user=request.user, post=post)  # якщо ще ні → додати

    return redirect("posts:feed")


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
    return redirect("posts:feed")

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
    post_id = comment.post.id
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Коментар видалено")
    return redirect("posts:feed")