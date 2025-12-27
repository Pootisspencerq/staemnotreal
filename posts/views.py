from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
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
        html = "".join(
            render_to_string(
                "posts/post_card.html",
                {"post": post, "user": request.user},
                request=request
            )
            for post in page_obj
        )
        return JsonResponse({"html": html, "has_next": page_obj.has_next()})

    return render(request, "posts/feed.html", {"page_obj": page_obj})


# -------------------------------
# ➕ CREATE POST
# -------------------------------
@login_required
@require_POST
def create_post(request):
    text = request.POST.get("text", "")
    file = request.FILES.get("file")
    link = request.POST.get("link", "")

    if not (text or file or link):
        return redirect("posts:feed")

    Post.objects.create(
        author=request.user,
        text=text,
        file=file,
        link=link,
        is_public=True,
        is_chat_message=False
    )

    return redirect("posts:feed")


# -------------------------------
# ❤️ LIKE (AJAX OK)
# -------------------------------
@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )

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
            async_to_sync(get_channel_layer().group_send)(
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

    return JsonResponse({
        "liked": liked,
        "likes": post.likes.count(),  # 🔥 FIX
    })



# -------------------------------
# ❌ DELETE POST (NO AJAX)
# -------------------------------
@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_staff:
        return HttpResponseForbidden()

    post.delete()
    return redirect("posts:feed")


# -------------------------------
# 🔁 REPOST (NO AJAX)
# -------------------------------
@login_required
@require_POST
def repost_post(request, post_id):
    original = get_object_or_404(Post, id=post_id)

    # 🔒 Always repost the ORIGINAL
    if original.shared_from:
        original = original.shared_from

    # 🚫 Prevent duplicate reposts by same user
    already_reposted = Post.objects.filter(
        author=request.user,
        shared_from=original
    ).exists()

    if already_reposted:
        return JsonResponse({
            "success": False,
            "error": "already_reposted",
            "reposts": original.shares.count(),
        })

    Post.objects.create(
        author=request.user,
        shared_from=original,
        text=original.text,
        img=original.img,
        video=original.video,
        file=original.file,
        link=original.link,
        is_public=True,
    )

    return JsonResponse({
        "success": True,
        "reposts": original.shares.count(),
    })


# -------------------------------
# 💬 COMMENT (AJAX OK)
# -------------------------------
@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    data = json.loads(request.body)
    text = data.get("text", "").strip()

    if not text:
        return JsonResponse({"success": False}, status=400)

    comment = Comment.objects.create(post=post, author=request.user, text=text)

    if post.author != request.user:
        notif = Notification.objects.create(
            recipient=post.author,
            actor=request.user,
            verb="commented on your post",
            target_post=post
        )
        async_to_sync(get_channel_layer().group_send)(
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
# 🔼⬇️ VOTE (AJAX OK)
# -------------------------------
@login_required
@require_POST
def vote_post(request, post_id, action):
    post = get_object_or_404(Post, id=post_id)

    vote_value = 1 if action == "up" else -1

    vote, created = Vote.objects.get_or_create(
        user=request.user,
        post=post,
        defaults={"vote_value": vote_value}
    )

    if not created:
        if vote.vote_value == vote_value:
            vote.delete()
        else:
            vote.vote_value = vote_value
            vote.save()

    score = post.votes.aggregate(
        total=Sum("vote_value")
    )["total"] or 0

    return JsonResponse({
        "score": score
    })



# -------------------------------
# 📄 POST DETAIL
# -------------------------------
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.liked_by_user = post.likes.filter(user=request.user).exists()
    post.vote_score = post.votes.aggregate(total=Sum("vote_value"))["total"] or 0

    return render(request, "posts/post_detail.html", {
        "post": post,
        "comments": post.comments.select_related("author")
    })
# -------------------------------
# ❌ DELETE COMMENT
# -------------------------------
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author and not request.user.is_staff:
        return HttpResponseForbidden()

    comment.delete()
    return JsonResponse({"success": True})


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
        return redirect("posts:feed")

    return render(request, "posts/edit_post.html", {"post": post})
