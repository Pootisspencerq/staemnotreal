from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .forms import ProfileForm
from .models import Profile, Follow
from django.contrib.auth import get_user_model

@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

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
            "is_following": is_following,
        },
    )
User = get_user_model()

@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    return render(request, 'profiles/detail.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', profile.bio)
        profile.save()
        return redirect('profiles:detail', username=request.user.username)
    return render(request, 'profiles/edit.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:my_profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # авто-логін після реєстрації
            return redirect("posts:feed")  # можна замінити на свою домашню сторінку
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


# -------------------
# Нове: підписки
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
