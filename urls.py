from django.contrib import admin
from django.urls import path, include
from staem_home import home
from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve
from mimetypes import add_type

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),

    # Homepage
    path("", home, name="home"),

    # Core apps
    path("accounts/", include("accounts.urls")),  # Login / Register / Profile
    path("posts/", include("posts.urls")),        # Feed & posts
    path("chat/", include("chat.urls")),          # Messaging

    # Other apps
    path("groups/", include("groups.urls")),          
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ Fix Chrome forcing .mp3/.wav download instead of playing
add_type("audio/mpeg", ".mp3", True)
add_type("audio/wav", ".wav", True)
