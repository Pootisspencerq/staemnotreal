# staemnotreal/notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('dropdown/', views.ajax_dropdown, name='dropdown'),
    path('unread-count/', views.ajax_unread_count, name='ajax_unread_count'),
    path('mark-all/', views.mark_read, name='mark_all'),
    path('ajax/mark-as-read/<int:pk>/', views.ajax_mark_as_read, name='ajax_mark_as_read'),
    path('mark-as-read/<int:pk>/', views.MarkAsReadView.as_view(), name='mark_read_single'),
]
