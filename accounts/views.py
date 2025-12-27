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


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)

    # ======================
    # POSTS (original)
    # ======================
    posts = Post.objects.filter(
        author=profile_user,
        shared_from__isnull=True
    ).order_by("-created_at")

    # ======================
    # REPOSTS
    # ======================
    reposts = Post.objects.filter(
        author=profile_user,
        shared_from__isnull=False
    ).order_by("-created_at")

    # ======================
    # LIKE + VOTE DATA
    # ======================
    if request.user.is_authenticated:
        for post in posts:
            post.liked_by_user = post.likes.filter(user=request.user).exists()
            post.vote_score = post.votes.aggregate(
                total=Sum("vote_value")
            )["total"] or 0

        for post in reposts:
            post.liked_by_user = post.likes.filter(user=request.user).exists()
            post.vote_score = post.votes.aggregate(
                total=Sum("vote_value")
            )["total"] or 0
    else:
        for post in posts:
            post.liked_by_user = False
            post.vote_score = post.votes.aggregate(
                total=Sum("vote_value")
            )["total"] or 0

        for post in reposts:
            post.liked_by_user = False
            post.vote_score = post.votes.aggregate(
                total=Sum("vote_value")
            )["total"] or 0

    # ======================
    # FRIENDS
    # ======================
    is_friend = False
    sent_request = None
    received_request = None

    if request.user.is_authenticated and request.user != profile_user:
        is_friend = (
            Friendship.objects.filter(user1=request.user, user2=profile_user).exists()
            or Friendship.objects.filter(user1=profile_user, user2=request.user).exists()
        )

        sent_request = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=profile_user
        ).first()

        received_request = FriendRequest.objects.filter(
            from_user=profile_user,
            to_user=request.user
        ).first()

    # ======================
    # CONTEXT (CRITICAL)
    # ======================
    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "profile": profile,

        # 🔥 ОБОВʼЯЗКОВО
        "posts": posts,
        "reposts": reposts,

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
def delete_cover(request):
    profile = request.user.profile
    if request.method == 'POST':
        if profile.cover:
            profile.cover.delete(save=True)
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'accounts/delete_cover.html')


@login_required
def delete_avatar(request):
    profile = request.user.profile
    if not profile.avatar:
        return redirect('accounts:profile', username=request.user.username)
    if request.method == 'POST':
        profile.avatar.delete(save=True)
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'accounts/delete_avatar.html')
