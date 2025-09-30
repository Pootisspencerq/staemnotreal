from django.urls import path
from .views import feed_view, create_post

app_name = "posts"

urlpatterns = [
    path("feed/", feed_view, name="feed"),
    path("create/", create_post, name="create"),
]
