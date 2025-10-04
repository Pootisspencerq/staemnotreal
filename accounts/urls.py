from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = "accounts"

urlpatterns = [


    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views.register_view, name="register"),
    path("edit/", views.edit_profile_view, name="edit_profile"),
    path("profile/", views.profile_view, name="my_profile"),  
    path("follow/<str:username>/", views.follow_user, name="follow"),
    path("unfollow/<str:username>/", views.unfollow_user, name="unfollow"),
    path('<str:username>/', views.profile_detail, name='detail'),
]
