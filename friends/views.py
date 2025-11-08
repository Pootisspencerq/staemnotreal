from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friendship

User = get_user_model()

@login_required
def list_requests(request):
    incoming = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    outgoing = FriendRequest.objects.filter(from_user=request.user, accepted=False)
    friends = Friendship.objects.filter(user1=request.user) | Friendship.objects.filter(user2=request.user)
    return render(request, 'friends/requests_list.html', {
        'incoming': incoming,
        'outgoing': outgoing,
        'friends': friends,
    })

@login_required
def send_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect('friends:list_requests')

@login_required
def accept_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, id=fr_id, to_user=request.user)
    fr.accepted = True
    fr.save()
    Friendship.objects.get_or_create(user1=fr.from_user, user2=fr.to_user)
    return redirect('friends:list_requests')
