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
    incoming = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    outgoing = FriendRequest.objects.filter(from_user=request.user, accepted=False)
    return render(request, "friends/friend_requests.html", {"incoming": incoming, "outgoing": outgoing})


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
    req = get_object_or_404(FriendRequest, id=req_id, to_user=request.user)

    Friendship.objects.get_or_create(user1=req.from_user, user2=req.to_user)
    req.accepted = True
    req.save()

    messages.success(request, "Додано у друзі ✔")
    return redirect("friends:requests")


@login_required
def delete_friend(request, user_id):
    Friendship.objects.filter(user1=request.user, user2=user_id).delete()
    Friendship.objects.filter(user2=request.user, user1=user_id).delete()

    messages.success(request, "Друг видалений")
    return redirect("friends:list")
