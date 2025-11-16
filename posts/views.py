from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from .models import Post, Like, Comment, Vote
from itertools import chain
import json

User = get_user_model()


# ✏️ Редагування поста
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":
        text = request.POST.get("text", "")
        link = request.POST.get("link", "")
        file = request.FILES.get("file")

        post.text = text
        post.link = link
        if file:
            post.file = file
        post.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Пост оновлено!"})

        return redirect("posts:feed")

    return render(request, "posts/edit_post.html", {"post": post})


# ❤️ Тогл лайка
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

    like_count = post.likes.count()
    return JsonResponse({'success': True, 'liked': liked, 'like_count': like_count})


# 📰 Головна стрічка
@login_required
def feed_view(request):
    if request.method == "POST":
        text = request.POST.get("text")
        file = request.FILES.get("file")
        link = request.POST.get("link")

        if text or file or link:
            post = Post.objects.create(
                author=request.user,
                text=text,
                file=file,
                link=link
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "post_id": post.id})

        return redirect("posts:feed")

    # ВСІ пости (в т.ч. репости)
    posts = Post.objects.select_related("author", "shared_from__author") \
        .prefetch_related("comments", "likes", "votes")

    posts = posts.filter(is_public=True)

    # Сортуємо за created_at (репости теж мають свій created_at)
    posts = posts.order_by("-created_at")

    for post in posts:
        post.liked_by_user = post.likes.filter(user=request.user).exists()
        post.vote_score = post.votes.aggregate(total=Sum('vote_value'))['total'] or 0

    return render(request, "posts/feed.html", {"posts": posts})


# ➕ Створення поста
@login_required
@require_POST
def create_post(request):
    text = request.POST.get("text")
    file = request.FILES.get("file")
    link = request.POST.get("link")

    if not (text or file or link):
        return JsonResponse({"success": False, "error": "Порожній пост"}, status=400)

    post = Post.objects.create(
        author=request.user,
        text=text,
        file=file,
        link=link
    )

    html = render_to_string("posts/_post_card.html", {"post": post, "user": request.user}, request=request)
    return JsonResponse({"success": True, "post_html": html})


# 💬 Коментар
@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    data = json.loads(request.body)
    text = data.get('text', '').strip()

    if not text:
        return JsonResponse({'success': False, 'error': 'Порожній коментар'}, status=400)

    comment = Comment.objects.create(post=post, author=request.user, text=text)

    profile = getattr(request.user, 'profile', None)
    avatar_url = profile.avatar.url if profile and profile.avatar else '/static/images/default-avatar.png'

    return JsonResponse({
        'success': True,
        'comment_id': comment.id,
        'author': request.user.username,
        'text': comment.text,
        'avatar': avatar_url
    })


# ❌ Видалити пост
@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Недостатньо прав'}, status=403)

    post.delete()
    return JsonResponse({'success': True})


# ❌ Видалити коментар
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Недостатньо прав'}, status=403)

    comment.delete()
    return JsonResponse({'success': True})


# 🔁 Репост (НОВИЙ МЕХАНІЗМ)
@login_required
@require_POST
def repost_post(request, post_id):
    original = get_object_or_404(Post, id=post_id)

    # Перевіряємо чи користувач вже репостив цей пост
    already = Post.objects.filter(author=request.user, shared_from=original).exists()
    if already:
        return JsonResponse({'success': False, 'message': 'Ви вже репостили цей пост.'})

    # Створюємо новий пост-репост
    repost = Post.objects.create(
        author=request.user,
        shared_from=original,
        text="",   # можна зробити коментар до репоста
        is_public=True
    )

    return JsonResponse({'success': True, 'message': 'Пост репостнуто!', 'repost_id': repost.id})


# 🔼⬇️ Голосування
@login_required
@require_POST
def vote_post(request, post_id, action):
    post = get_object_or_404(Post, id=post_id)
    value = 1 if action == 'up' else -1

    Vote.objects.update_or_create(
        user=request.user,
        post=post,
        defaults={'vote_value': value}
    )

    score = post.votes.aggregate(total=Sum('vote_value'))['total'] or 0
    return JsonResponse({'success': True, 'score': score})


# 📄 Деталі поста
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.liked_by_user = post.likes.filter(user=request.user).exists()
    post.vote_score = post.votes.aggregate(total=Sum('vote_value'))['total'] or 0

    comments = post.comments.select_related("author")

    return render(request, "posts/post_detail.html", {
        "post": post,
        "comments": comments
    })
