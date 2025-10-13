from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
from django.views.decorators.http import require_http_methods
from .forms import MessageForm
@login_required
def inbox(request):
    # список чатів користувача
    chats = request.user.chats.all()
    return render(request, 'chat/inbox.html', {"chats": chats})

@login_required
def chat_detail(request, chat_id):
    chat, created = Chat.objects.get_or_create(
        id=chat_id,
        defaults={"name": "Глобальний чат"}
    )

    if request.user not in chat.participants.all():
        chat.participants.add(request.user)

    form = MessageForm()
    return render(request, 'chat/detail.html', {"chat": chat, "form": form})


def chat_view(request):
    chat, created = Chat.objects.get_or_create(id=1)  # глобальний чат
    if request.user.is_authenticated:
        chat.participants.add(request.user)  # додаємо користувача
    return render(request, "chat/chat_detail.html", {"chat": chat})

@login_required
def messages_api(request, chat_id):
    """
    GET -> повернути останні 50 повідомлень як JSON
    POST -> створити повідомлення (з file у request.FILES для attachment)
    """
    chat = get_object_or_404(Chat, pk=chat_id)

    # Переконуємося, що користувач є учасником чату
    if request.user not in chat.participants.all():
        chat.participants.add(request.user)

    if request.method == "GET":
        msgs = chat.messages.select_related("author").all().order_by("-created_at")[:50]
        data = []
        for m in reversed(msgs):
            data.append({
                "id": m.id,
                "author_id": m.author.id,
                "author_username": m.author.get_username(),
                "message": m.text,  # правильне поле
                "attachment_url": m.attachment.url if m.attachment else None,
                "created_at": m.created_at.isoformat(),
            })
        return JsonResponse({"messages": data})

    elif request.method == "POST":
        content = request.POST.get("message", "").strip()
        image = request.FILES.get("image")  # замість attachment
        m = Message.objects.create(chat=chat, author=request.user, text=content, image=image)
        return JsonResponse({
            "id": m.id,
            "author_id": m.author.id,
            "author_username": m.author.get_username(),
            "message": m.text,
            "image_url": m.image.url if m.image else None,  # URL фото
            "created_at": m.created_at.isoformat(),
        }, status=201)

    else:
        return JsonResponse({"error": "method not allowed"}, status=405)
