# notifications/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .models import Notification


class MarkAsReadView(View):
    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return redirect('notifications:list')


@login_required
def notification_page(request):
    """
    Full page showing user's notifications (useable via /notifications/).
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'notifications/notifications_page.html', {'notifications': notifications})


@login_required
def ajax_dropdown(request):
    """
    Return HTML fragment for dropdown (latest 10).
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:10]
    html = render_to_string(
        'notifications/notifications_dropdown.html',
        {'notifications': notifications, 'user': request.user},
        request=request
    )
    return JsonResponse({'html': html})


@login_required
def ajax_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})


@login_required
@require_POST
def ajax_mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'ok': True, 'pk': pk})


@login_required
@require_POST
def ajax_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})
