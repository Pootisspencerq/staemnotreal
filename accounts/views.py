from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum
from .forms import ProfileForm
from .models import Profile
from friends.models import FriendRequest, Friendship
from posts.models import Post

User = get_user_model()


# -------------------
# 🔹 Реєстрація
# -------------------
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Акаунт створено успішно!")
            return redirect("posts:feed")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


# -------------------
# 🔹 Вихід
# -------------------
def logout_view(request):
    logout(request)
    return redirect("/")


# -------------------
# 🔹 Профіль користувача
# -------------------
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)

    # Посты
    posts = Post.objects.filter(
        author=profile_user,
        shared_from__isnull=True
    ).order_by("-created_at")

    # Репосты
    reposts = Post.objects.filter(
        author=profile_user,
        shared_from__isnull=False
    ).order_by("-created_at")

    # Лайки и голоса
    for post in posts:
        post.liked_by_user = post.likes.filter(user=request.user).exists()
        post.vote_score = post.votes.aggregate(total=Sum("vote_value")).get("total") or 0

    for post in reposts:
        post.liked_by_user = post.likes.filter(user=request.user).exists()
        post.vote_score = post.votes.aggregate(total=Sum("vote_value")).get("total") or 0

    # ДРУЗІ — ПОКИ СТАТИКА
    is_friend = False
    sent_request = None
    received_request = None

    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "profile": profile,

        "posts": posts,
        "reposts": reposts,   # 🔥 ДОДАНО — тепер репости працюють

        "is_friend": is_friend,
        "sent_request": sent_request,
        "received_request": received_request,
    })


# -------------------
# 🔹 Редагування профілю
# -------------------
@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено!")
            return redirect("accounts:profile", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {
        "form": form,
        "user_profile": profile,   # 🔥 ДОДАНО
    })

@login_required
def delete_avatar(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.avatar:
        profile.avatar.delete(save=True)

    return redirect("accounts:edit_profile")


@login_required
def delete_cover(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.cover:
        profile.cover.delete(save=True)

    return redirect("accounts:edit_profile")