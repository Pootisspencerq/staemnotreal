from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Post
from accounts.models import Follow

User = get_user_model()


@login_required
def feed_view(request):
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Post.objects.create(author=request.user, text=text)  # 🔹 тут

            return redirect("posts:feed")

    following_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)

    posts = Post.objects.select_related("author").filter(
        author__in=list(following_ids) + [request.user.id]
    ).order_by("-created_at")

    return render(request, "posts/feed.html", {"posts": posts})


@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Post.objects.create(author=request.user, text=text)  # 🔹 і тут

        return redirect("posts:feed")
    return redirect("posts:feed")
