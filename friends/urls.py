from django.urls import path
from . import views 
app_name = "friends"  # ← МАЄ БУТИ СТОВІДСОТКОВО!

urlpatterns = [
    path("", views.friends_list, name="list"),
    path("requests/", views.friend_requests, name="requests"),
    path("send/<int:user_id>/", views.send_request, name="send"),
    path('accept/<int:req_id>/', views.accept_request, name='accept'),
    path('remove/<int:user_id>/', views.remove_friend, name='remove'),
    path('cancel/<int:req_id>/', views.remove_request, name='cancel'), 
]