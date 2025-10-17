from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification
from django.views import View
class MarkAsReadView(View):
    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        # після позначення як прочитане — повертаємо користувача назад
        return redirect('notifications:list')
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notifications_list.html', {
        'notifications': notifications
    })


@login_required
def mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.mark_as_read()
    return redirect(request.META.get('HTTP_REFERER', '/notifications/'))
