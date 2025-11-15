from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from .models import Post, Like, Comment, Repost, Vote
from itertools import chain
import json

User = get_user_model()

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

    # Отримуємо оригінальні пости
    posts_qs = Post.objects.select_related("author").prefetch_related("comments", "likes", "reposts", "votes").filter(is_public=True)
    # Отримуємо репости
    reposts_qs = Repost.objects.select_related('user', 'original_post__author').all()

    # Конвертуємо репости в об'єкти постів з додатковими атрибутами
    repost_posts = []
    for r in reposts_qs:
        p = r.original_post
        p.reposted_by = r.user
        p.repost_created_at = r.created_at
        repost_posts.append(p)

    # Об'єднуємо пости і репости хронологічно
    all_posts = sorted(
        chain(posts_qs, repost_posts),
        key=lambda x: getattr(x, 'created_at', getattr(x, 'repost_created_at', None)),
        reverse=True
    )

    for post in all_posts:
        post.liked_by_user = post.likes.filter(user=request.user).exists()
        post.vote_score = post.votes.aggregate(total=Sum('vote_value'))['total'] or 0

    return render(request, "posts/feed.html", {"posts": all_posts})

# ➕ Створення поста (окремо для AJAX)
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

# ❤️ Лайк / анлайк
@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    liked, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        liked.delete()
        post.like_count = max(0, post.likes.count())
        return JsonResponse({'success': True, 'liked': False, 'like_count': post.like_count})

    post.like_count = post.likes.count()
    return JsonResponse({'success': True, 'liked': True, 'like_count': post.like_count})

# 💬 Додати коментар
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
    if profile and profile.avatar and hasattr(profile.avatar, 'url'):
        avatar_url = profile.avatar.url
    else:
        avatar_url = '/static/images/default-avatar.png'

    return JsonResponse({
        'success': True,
        'comment_id': comment.id,
        'author': request.user.username,
        'text': comment.text,
        'avatar': avatar_url
    })

# ❌ Видалення поста (AJAX)
@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Недостатньо прав'}, status=403)

    post.delete()
    return JsonResponse({'success': True})

# ❌ Видалення коментаря (AJAX)
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Недостатньо прав'}, status=403)

    comment.delete()
    return JsonResponse({'success': True})

# 🔁 Репост
@login_required
@require_POST
def repost_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    already = Repost.objects.filter(user=request.user, original_post=post).exists()

    if already:
        return JsonResponse({'success': False, 'message': 'Ви вже репостили цей пост.'})

    Repost.objects.create(user=request.user, original_post=post)
    return JsonResponse({'success': True, 'message': 'Пост репостнуто!'})

# 🔼⬇️ Голосування (up/down)
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

    return render(request, "posts/post_detail.html", {"post": post, "comments": comments})
