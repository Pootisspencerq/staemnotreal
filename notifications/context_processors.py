# notifications/context_processors.py
from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:10]
    else:
        notifications = []
    return {'notifications': notifications}


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {"unread_count": 0, "latest_notifications": []}

    qs = request.user.notifications.all().order_by("-timestamp")

    latest = []
    for n in qs[:5]:
        latest.append({
            "id": n.id,
            "verb": getattr(n, "verb", str(n)),
            "link": getattr(n, "link", "#"),
            "timestamp": n.timestamp,
            "is_read": n.is_read
        })

    unread_count = request.user.notifications.filter(is_read=False).count()

    return {"unread_count": unread_count, "latest_notifications": latest}
