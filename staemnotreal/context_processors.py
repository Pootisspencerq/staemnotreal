from notifications.models import Notification
from friends.models import FriendRequest
def unread_notifications(request):
    if request.user.is_authenticated:
        notes = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        return {
            'notifications': notes,
            'unread_notifications_count': notes.count(),
        }
    return {'notifications': [], 'unread_notifications_count': 0}

def friend_requests_context(request):
    """Передає вхідні запити в друзі для navbar dropdown"""
    if request.user.is_authenticated:
        incoming = FriendRequest.objects.filter(to_user=request.user , accepted=False)
        return {
            'friend_requests': incoming,
            'friend_requests_count': incoming.count(),
        }
    return {'friend_requests': [], 'friend_requests_count': 0}
