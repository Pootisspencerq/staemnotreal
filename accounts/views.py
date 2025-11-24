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

    # 🔥 Один список постів (і звичайні, і репости)
    posts = Post.objects.filter(
        author=profile_user
    ).order_by("-created_at").select_related("author", "shared_from")

    # 🔥 Обчислення даних (лайки, голоси)
    for post in posts:
        post.liked_by_user = post.likes.filter(user=request.user).exists()
        post.vote_score = post.votes.aggregate(total=Sum("vote_value")).get("total") or 0

    # TODO: тут буде нормальна система друзів
    is_friend = False
    sent_request = None
    received_request = None

    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "profile": profile,
        "posts": posts,
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

    return render(request, "accounts/edit_profile.html", {"form": form})
