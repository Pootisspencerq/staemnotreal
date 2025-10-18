from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notifications.models import Notification

@login_required
def home(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:10]
    return render(request, 'home.html', {'notifications': notifications})
