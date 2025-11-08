from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Message

User = get_user_model()

@login_required
def chat_list(request):
    # Всі користувачі, крім себе
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/chat_list.html', {'users': users})

@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Всі повідомлення між двома користувачами
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            Message.objects.create(sender=request.user, receiver=other_user, text=text)
            return redirect('chat:detail', user_id=other_user.id)

    return render(request, 'chat/chat_detail.html', {
        'other_user': other_user,
        'messages': messages,
    })
