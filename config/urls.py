from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def home(request):
    return HttpResponse("<h1>Welcome to Social Network!</h1>")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),  # головна сторінка
    path("profiles/", include("profiles.urls")),
    path("groups/", include("groups.urls")),
    path("chat/", include("chat.urls")),
    path("notifications/", include("notifications.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
