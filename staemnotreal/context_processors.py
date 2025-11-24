from notifications.models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        notes = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        return {
            'notifications': notes,
            'unread_notifications_count': notes.count(),
        }
    return {'notifications': [], 'unread_notifications_count': 0}
