from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .forms import ProfileForm
from .models import Profile, Follow

User = get_user_model()

# -------------------
# Реєстрація
# -------------------
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # авто-логін після реєстрації
            messages.success(request, "Акаунт створено успішно!")
            return redirect("posts:feed")  # заміни на свою домашню
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


# -------------------
# Профіль
# -------------------
@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)

    # Перевірка чи request.user вже підписаний
    is_following = False
    if request.user.is_authenticated and user != request.user:
        is_following = Follow.objects.filter(
            follower=request.user, following=user
        ).exists()

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": user,
            "profile": profile,
            "is_following": is_following,
        },
    )


@login_required
def edit_profile(request):
    # Ensure profile exists
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


# -------------------
# Підписки
# -------------------
@login_required
def follow_user(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        Follow.objects.get_or_create(follower=request.user, following=target)
    return redirect("accounts:profile", username=target.username)


@login_required
def unfollow_user(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        Follow.objects.filter(follower=request.user, following=target).delete()
    return redirect("accounts:profile", username=target.username)
