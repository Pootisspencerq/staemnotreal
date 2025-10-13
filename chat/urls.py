from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.inbox, name="inbox"),                # список чатів
    path("chat/<int:chat_id>/", views.chat_detail, name="chat_detail"),  # деталі чату
    path("api/chat/<int:chat_id>/messages/", views.messages_api, name="messages_api"),
]