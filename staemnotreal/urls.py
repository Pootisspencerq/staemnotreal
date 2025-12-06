from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .staem_home import home_view

urlpatterns = [

    # --- Admin ---
    path('admin/', admin.site.urls),

    # --- Accounts (логін, реєстрація, профіль) ---
    path('accounts/', include('accounts.urls')),

    # --- Posts / Feed / Likes / Comments ---
    path('posts/', include('posts.urls', namespace='posts')),

    # --- Friends system ---
    path('friends/', include('friends.urls')),

    # --- Groups system ---
    path('groups/', include('groups.urls', namespace='groups')),

    # --- Chat / WebSockets ---
    path('chat/', include('chat.urls', namespace='chat')),

    # --- Notifications ---
    path('notifications/', include('notifications.urls')),
    path("friends/", include("friends.urls", namespace="friends")),

    # --- Головна сторінка (редірект на стрічку) ---
    path('', home_view, name='home'),
]

# --- DEBUG static/media serving ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
