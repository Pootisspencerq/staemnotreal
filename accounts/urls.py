from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("edit/", views.edit_profile, name="edit_profile"),

    # Друзі
    path("friends/", views.friends_list, name="friends_list"),
    path("friend-requests/", views.friend_requests_list, name="friend_requests_list"),
    path("send-friend-request/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("cancel-friend-request/<int:fr_id>/", views.cancel_friend_request, name="cancel_friend_request"),
    path("accept-friend-request/<int:fr_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("decline-friend-request/<int:fr_id>/", views.decline_friend_request, name="decline_friend_request"),
    path("remove-friend/<int:user_id>/", views.remove_friend, name="remove_friend"),
    path("<str:username>/", views.profile_detail, name="profile"),
]
