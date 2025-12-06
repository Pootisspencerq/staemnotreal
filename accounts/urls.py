from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("edit/", views.edit_profile, name="edit_profile"),

    path('delete-cover/', views.delete_cover, name='delete_cover'),
    path('delete-avatar/', views.delete_avatar, name='delete_avatar'),

    path("<str:username>/", views.profile_view, name="profile"),
]
