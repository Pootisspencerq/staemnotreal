# staemnotreal/notifications/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST


class MarkAsReadView(View):
    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.unread = False
        notification.save()
        return redirect('notifications:list')


@login_required
def ajax_list(request):
    unread_count = Notification.objects.filter(recipient=request.user, unread=True).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def mark_read(request):
    """Позначає всі сповіщення як прочитані"""
    Notification.objects.filter(recipient=request.user, unread=True).update(unread=False)
    return JsonResponse({'status': 'ok'})


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'notifications/notifications_list.html', {
        'notifications': notifications
    })


@login_required
@require_POST
def ajax_mark_as_read(request, pk):
    """AJAX: помітити конкретне сповіщення як прочитане"""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.unread = False
    notif.save()
    return JsonResponse({'ok': True, 'pk': pk})


@login_required
def ajax_unread_count(request):
    """AJAX: повернути кількість непрочитаних"""
    count = Notification.objects.filter(recipient=request.user, unread=True).count()
    return JsonResponse({'unread_count': count})


@login_required
def ajax_dropdown(request):
    """AJAX: повернути HTML для випадаючого списку сповіщень"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:10]
    html = render_to_string(
        'notifications/notifications_dropdown.html',
        {'notifications': notifications, 'user': request.user},
        request=request
    )
    return JsonResponse({'html': html})
