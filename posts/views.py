from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post


@login_required
def feed_view(request):
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Post.objects.create(author=request.user, text=text)
            return redirect("feed")

    posts = Post.objects.select_related("author").all()
    return render(request, "posts/feed.html", {"posts": posts})

def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Post.objects.create(author=request.user, text=text)
        return redirect("posts:feed")
    return redirect("posts:feed")