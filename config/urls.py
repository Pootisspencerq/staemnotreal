from django.contrib import admin
from django.urls import path, include
from staem_home import home
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),

    # Homepage
    path("", home, name="home"),

    # Apps
    path("accounts/", include("accounts.urls")),  # handles login/logout/register/profile
    path("posts/", include("posts.urls")),        # feed & post URLs

    # Optional: other apps
    path("chat/", include("chat.urls")),
    path("groups/", include("groups.urls")),
    
    path("notifications/", include("notifications.urls")),
 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)