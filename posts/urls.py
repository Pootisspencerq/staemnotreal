from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("feed/", views.feed_view, name="feed"),
    path("<int:post_id>/", views.post_detail, name="detail"),  # ← added
    path("<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("<int:post_id>/repost/", views.repost_post, name="repost_post"),
    path('vote/<int:post_id>/<str:action>/', views.vote_post, name='vote_post'),
]
