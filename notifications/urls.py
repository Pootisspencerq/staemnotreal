from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),  # ← замість NotificationListView.as_view()


    path('<int:pk>/read/', views.MarkAsReadView.as_view(), name='mark_as_read'),
]
