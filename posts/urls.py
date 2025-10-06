from django.urls import path
from .views import (
    feed_view,
    create_post,
    toggle_like,
    add_comment,
    edit_post,
    delete_post,
    delete_comment,
)

app_name = "posts"

urlpatterns = [
    path("feed/", feed_view, name="feed"),
    path("create/", create_post, name="create"),
    path("<int:post_id>/like/", toggle_like, name="toggle_like"),
    path("<int:post_id>/comment/", add_comment, name="add_comment"),
    path("<int:post_id>/edit/", edit_post, name="edit_post"),
    path("<int:post_id>/delete/", delete_post, name="delete_post"),
    path("comment/<int:comment_id>/delete/", delete_comment, name="delete_comment"),
]
