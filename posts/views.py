from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

from .models import Post, Like, Comment, Vote
from notifications.models import Notification

ITEMS_PER_PAGE = 8

# -------------------------------
# 📜 FEED + INFINITE SCROLL
# -------------------------------
@login_required
def feed_view(request):
    posts = (
        Post.objects
        .select_related("author", "shared_from__author")
        .prefetch_related("comments", "likes", "votes")
        .filter(Q(is_chat_message=False) | Q(is_chat_message__isnull=True))
        .order_by("-created_at")
    )

    paginator = Paginator(posts, ITEMS_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = ""
        for post in page_obj:
            html += render_to_string(
                "posts/post_card.html",
                {"post": post, "user": request.user},
                request=request
            )
        return JsonResponse({"html": html, "has_next": page_obj.has_next()})

    return render(request, "posts/feed.html", {"page_obj": page_obj})

# -------------------------------
# ✏️ EDIT POST
# -------------------------------
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":
        post.text = request.POST.get("text", "")
        post.link = request.POST.get("link", "")

        file = request.FILES.get("file")
        if file:
            post.file = file

        post.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("posts:feed")

    return render(request, "posts/edit_post.html", {"post": post})

# -------------------------------
# ❤️ LIKE + NOTIFICATION + WS
# -------------------------------
@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

        if post.author != request.user:
            notif = Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb="liked your post",
                target_post=post
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{post.author.id}",
                {
                    "type": "notify",
                    "event": "new_notification",
                    "message": {
                        "actor": request.user.username,
                        "verb": notif.verb,
                        "post_id": post.id,
                        "timestamp": timezone.now().isoformat()
                    }
                }
            )

    return JsonResponse({"liked": liked, "like_count": post.likes.count()})

# -------------------------------
# ➕ CREATE POST (AJAX)
# -------------------------------
@login_required
@require_POST
def create_post(request):
    text = request.POST.get("text", "")
    file = request.FILES.get("file")
    link = request.POST.get("link", "")

    if not (text or file or link):
        return JsonResponse({"success": False, "error": "Empty post"}, status=400)

    post = Post.objects.create(
        author=request.user,
        text=text,
        file=file,
        link=link,
        is_public=True,
        is_chat_message=False,
        chat_thread=None,
        group=None
    )


    return redirect("posts:feed")   
# -------------------------------
# 💬 COMMENT + NOTIFICATIONS + WS
# -------------------------------
@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    data = json.loads(request.body)
    text = data.get("text", "").strip()

    if not text:
        return JsonResponse({"success": False, "error": "Empty"}, status=400)

    comment = Comment.objects.create(post=post, author=request.user, text=text)

    if post.author != request.user:
        notif = Notification.objects.create(
            recipient=post.author,
            actor=request.user,
            verb="commented on your post",
            target_post=post
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{post.author.id}",
            {
                "type": "notify",
                "event": "new_notification",
                "message": {
                    "actor": request.user.username,
                    "verb": notif.verb,
                    "post_id": post.id,
                    "timestamp": timezone.now().isoformat()
                }
            }
        )

    html = render_to_string("posts/_single_comment.html", {"comment": comment}, request=request)
    return JsonResponse({"success": True, "html": html})

# -------------------------------
# ❌ DELETE POST
# -------------------------------
@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_staff:
        return JsonResponse({"success": False}, status=403)

    post.delete()
    return JsonResponse({"success": True})

# -------------------------------
# ❌ DELETE COMMENT
# -------------------------------
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author and not request.user.is_staff:
        return JsonResponse({"success": False}, status=403)

    comment.delete()
    return JsonResponse({"success": True})

# -------------------------------
# 🔁 REPOST (with WS)
# -------------------------------
@login_required
@require_POST
def repost_post(request, post_id):
    original = get_object_or_404(Post, id=post_id)

    if Post.objects.filter(author=request.user, shared_from=original).exists():
        return JsonResponse({"success": False, "message": "Already reposted"})

    repost = Post.objects.create(author=request.user, shared_from=original, is_public=True)

    if original.author != request.user:
        notif = Notification.objects.create(
            recipient=original.author,
            actor=request.user,
            verb="reposted your post",
            target_post=original
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{original.author.id}",
            {
                "type": "notify",
                "event": "new_notification",
                "message": {
                    "actor": request.user.username,
                    "verb": notif.verb,
                    "post_id": original.id,
                    "timestamp": timezone.now().isoformat()
                }
            }
        )

    return JsonResponse({"success": True, "repost_id": repost.id})

# -------------------------------
# 🔼⬇️ VOTE
# -------------------------------
@login_required
@require_POST
def vote_post(request, post_id, action):
    post = get_object_or_404(Post, id=post_id)
    value = 1 if action == "up" else -1

    Vote.objects.update_or_create(user=request.user, post=post, defaults={"vote_value": value})

    score = post.votes.aggregate(total=Sum("vote_value"))["total"] or 0
    return JsonResponse({"success": True, "score": score})

# -------------------------------
# 📄 POST DETAIL
# -------------------------------
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.liked_by_user = post.likes.filter(user=request.user).exists()
    post.vote_score = post.votes.aggregate(total=Sum("vote_value"))["total"] or 0
    comments = post.comments.select_related("author")

    return render(request, "posts/post_detail.html", {
        "post": post,
        "comments": comments
    })
