# groups/urls.py
from django.urls import path
from . import views

app_name = "groups"



urlpatterns = [
    path("", views.group_list, name="list"),
    path("create/", views.group_create, name="create"),
    path("<int:group_id>/", views.group_detail, name="detail"),
    path("<int:group_id>/join/", views.join_group, name="join"),
    path("<int:group_id>/leave/", views.leave_group, name="leave"),
    path("<int:group_id>/delete/", views.group_delete, name="group_delete"),

]
