from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FriendRequest, Friendship
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def friends_list(request):
    friends = Friendship.get_friends(request.user)
    return render(request, "friends/friends_list.html", {"friends": friends})


@login_required
def friend_requests(request):
    incoming = FriendRequest.objects.filter(to_user=request.user)
    outgoing = FriendRequest.objects.filter(from_user=request.user)
    return render(request, "friends/friend_requests.html", {
        "incoming": incoming,
        "outgoing": outgoing
    })


@login_required
def send_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user == to_user:
        messages.error(request, "Неможливо додати себе!")
        return redirect("friends:list")

    req, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)

    if created:
        messages.success(request, "Запит відправлено ✔")
    else:
        messages.warning(request, "Запит уже існує")

    return redirect("friends:requests")


@login_required
def accept_request(request, req_id):
    if request.method == "POST":
        fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user)
        fr.accept()  # твоя логіка прийняття
        return redirect("friends:requests")
    return redirect("friends:requests")

@login_required
def remove_request(request, req_id):
    if request.method == "POST":
        fr = get_object_or_404(FriendRequest, id=req_id)
        if fr.from_user == request.user or fr.to_user == request.user:
            fr.delete()
        return redirect("friends:requests")
    return redirect("friends:requests")

@login_required
def remove_friend(request, user_id):
    if request.method == "POST":
        friend = get_object_or_404(User, id=user_id)
        # Видаляємо дружбу обом користувачам
        Friendship.remove_friend(request.user, friend)
        messages.success(request, f"{friend.username} більше не у твоїх друзях")
        return redirect("friends:list")
    return redirect("friends:list")
