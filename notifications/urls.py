from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('dropdown/', views.ajax_dropdown, name='dropdown'),
    path('', views.notification_list, name='list'),
    path('unread-count/', views.ajax_unread_count, name='ajax_unread_count'),  # <-- тут змінив
    path('mark-as-read/<str:pk>/', views.mark_read, name='mark_as_read'),
]
