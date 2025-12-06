from django.urls import path
from .views import friends_list, friend_requests, send_request, accept_request, delete_friend

app_name = "friends"  # ← МАЄ БУТИ СТОВІДСОТКОВО!

urlpatterns = [
    path("", friends_list, name="list"),
    path("requests/", friend_requests, name="requests"),
    path("send/<int:user_id>/", send_request, name="send"),
    path("accept/<int:req_id>/", accept_request, name="accept"),
    path("remove/<int:user_id>/", delete_friend, name="remove"),
]
