from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from .forms import ProfileForm
from .models import Profile
from friends.models import FriendRequest, Friendship  # твій модуль друзів

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
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)

    # Перевірка дружби
    is_friend = Friendship.objects.filter(
        Q(user1=request.user, user2=profile_user) |
        Q(user1=profile_user, user2=request.user)
    ).exists()

    # Перевірка запитів на дружбу
    sent_request = FriendRequest.objects.filter(from_user=request.user, to_user=profile_user).first()
    received_request = FriendRequest.objects.filter(from_user=profile_user, to_user=request.user).first()

    context = {
        "profile_user": profile_user,
        "profile": profile,
        "is_friend": is_friend,
        "sent_request": sent_request,
        "received_request": received_request,
    }
    return render(request, "accounts/profile.html", context)


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
