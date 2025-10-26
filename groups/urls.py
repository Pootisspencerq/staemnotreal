from django.urls import path
from . import views

app_name = "groups"

urlpatterns = [
    path("", views.group_list, name="list"),
    path("create/", views.create_group, name="create"),
    path("<int:pk>/", views.group_detail, name="detail"),
    path("<int:pk>/join/", views.join_group, name="join"),
    path("<int:pk>/leave/", views.leave_group, name="leave"),
    path("<int:pk>/delete_post/<int:post_id>/", views.delete_post, name="post_delete"),
    path("<int:pk>/create_post/", views.create_post, name="post_create"),
    path("<int:pk>/manage_moderators/", views.manage_moderators, name="manage_moderators"),
    path("<int:pk>/toggle_moderator/<int:user_id>/", views.toggle_moderator, name="toggle_moderator"),
    path("<int:pk>/delete/", views.delete_group, name="delete_group"),  # <-- Додано
]
