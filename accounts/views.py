from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import ProfileForm
from .models import Profile, Follow, FriendRequest

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
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)

    is_following = Follow.objects.filter(
        follower=request.user, following=user
    ).exists() if user != request.user else False

    # Дружба
    is_friend = False
    if hasattr(request.user, "profile"):
        is_friend = profile in request.user.profile.friends.all()

    # Поточний запит дружби (у будь-якому напрямку)
    friend_request = FriendRequest.objects.filter(
        from_user=request.user, to_user=user
    ).first() or FriendRequest.objects.filter(
        from_user=user, to_user=request.user
    ).first()

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": user,
            "profile": profile,
            "is_following": is_following,
            "is_friend": is_friend,
            "friend_request": friend_request,
        },
    )


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


# -------------------
# 🔹 ДРУЗІ
# -------------------
@login_required
def send_friend_request(request, user_id):
    """Надсилання запиту в друзі"""
    if request.user.id == int(user_id):
        messages.error(request, "Ви не можете додати в друзі самого себе.")
        return redirect("accounts:profile", username=request.user.username)

    to_user = get_object_or_404(User, id=user_id)

    # Якщо вже друзі — не створюємо запит
    if to_user.profile in request.user.profile.friends.all():
        messages.info(request, "Ви вже друзі.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    fr, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=to_user
    )

    if not created:
        messages.info(request, "Запит у друзі вже існує.")
    else:
        messages.success(request, "Запит у друзі надіслано.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def cancel_friend_request(request, fr_id):
    """Скасувати запит"""
    fr = get_object_or_404(FriendRequest, id=fr_id, from_user=request.user)
    fr.cancel()
    messages.success(request, "Запит у друзі скасовано.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def accept_friend_request(request, fr_id):
    """Прийняти запит у друзі"""
    fr = get_object_or_404(FriendRequest, id=fr_id, to_user=request.user, status="pending")
    fr.accept()
    messages.success(request, f"Тепер ви друзі з {fr.from_user.username}.")
    return redirect("accounts:friend_requests_list")


@login_required
def decline_friend_request(request, fr_id):
    """Відхилити запит"""
    fr = get_object_or_404(FriendRequest, id=fr_id, to_user=request.user, status="pending")
    fr.decline()
    messages.success(request, "Запит у друзі відхилено.")
    return redirect("accounts:friend_requests_list")


@login_required
def remove_friend(request, user_id):
    """Видалити друга"""
    other = get_object_or_404(User, id=user_id)
    try:
        request.user.profile.remove_friend(other.profile)
    except Exception as e:
        messages.error(request, f"Помилка при видаленні друга: {e}")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    messages.success(request, "Користувача видалено зі списку друзів.")
    return redirect("accounts:friends_list")


@login_required
def friends_list(request):
    """Список друзів поточного користувача"""
    friends = getattr(request.user.profile, "friends", []).all()
    return render(request, "accounts/friends_list.html", {"friends": friends})


@login_required
def friend_requests_list(request):
    """Вхідні та вихідні запити"""
    incoming = FriendRequest.objects.filter(to_user=request.user, status="pending")
    outgoing = FriendRequest.objects.filter(from_user=request.user, status="pending")
    return render(
        request,
        "accounts/friend_requests.html",
        {"incoming": incoming, "outgoing": outgoing},
    )
