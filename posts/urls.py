from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    # 📜 Головна стрічка
    path("", views.feed_view, name="feed"),  # /posts/

    # 🧾 Деталі поста
    path("<int:post_id>/", views.post_detail, name="detail"),  # /posts/1/

    # ❤️ Лайк / анлайк
    path("<int:post_id>/like/", views.toggle_like, name="toggle_like"),

    # 💬 Коментарі
    path("<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("create/", views.create_post, name="create_post"),

    # ✏️ Редагування / видалення поста
    path("<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("<int:post_id>/delete/", views.delete_post, name="delete_post"),

    # 🔁 Репост
    path("<int:post_id>/repost/", views.repost_post, name="repost_post"),

    # ⬆️⬇️ Голосування
    path("vote/<int:post_id>/<str:action>/", views.vote_post, name="vote_post"),

]
