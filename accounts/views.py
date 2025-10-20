from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from .forms import ProfileForm
from .models import Profile, Follow, FriendRequest
User = get_user_model()

# -------------------
# Реєстрація
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
 

def logout_view(request):
    logout(request)
    return redirect('/')

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
def send_friend_request(request, user_id):
    if request.user.id == int(user_id):
        messages.error(request, "You cannot friend yourself.")
        return redirect('profile', pk=user_id)
    to_user = get_object_or_404(User, id=user_id)
    fr, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    if not created:
        messages.info(request, "Friend request already exists.")
    else:
        messages.success(request, "Friend request sent.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def cancel_friend_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, id=fr_id, from_user=request.user)
    fr.cancel()
    messages.success(request, "Friend request cancelled.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def accept_friend_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, id=fr_id, to_user=request.user, status='pending')
    fr.accept()
    messages.success(request, f"You are now friends with {fr.from_user.username}.")
    return redirect('friend_requests_list')

@login_required
def decline_friend_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, id=fr_id, to_user=request.user, status='pending')
    fr.decline()
    messages.success(request, "Friend request declined.")
    return redirect('friend_requests_list')

@login_required
def remove_friend(request, user_id):
    other = get_object_or_404(User, id=user_id)
    # Try using profile.friends
    try:
        request.user.profile.friends.remove(other.profile)
        other.profile.friends.remove(request.user.profile)
    except Exception:
        if hasattr(request.user, 'friends'):
            request.user.friends.remove(other)
            other.friends.remove(request.user)
    messages.success(request, "Friend removed.")
    return redirect('friends_list')

@login_required
def friends_list(request):
    # try profile version
    try:
        friends = request.user.profile.friends.all()
    except Exception:
        friends = request.user.friends.all() if hasattr(request.user, 'friends') else []
    return render(request, 'accounts/friends_list.html', {'friends': friends})

@login_required
def friend_requests_list(request):
    incoming = FriendRequest.objects.filter(to_user=request.user, status='pending')
    outgoing = FriendRequest.objects.filter(from_user=request.user, status='pending')
    return render(request, 'accounts/friend_requests.html', {'incoming': incoming, 'outgoing': outgoing})