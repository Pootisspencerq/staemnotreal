from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Аутентифікація
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views.register_view, name="register"),

    # Профіль
    path("edit/", views.edit_profile, name="edit_profile"),
    path("<str:username>/", views.profile_detail, name="profile"),

    # Підписки
    path("<str:username>/follow/", views.follow_user, name="follow"),
    path("<str:username>/unfollow/", views.unfollow_user, name="unfollow"),
]
