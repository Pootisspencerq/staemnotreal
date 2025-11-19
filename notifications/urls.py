# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_page, name='list'),            # full-page list
    path('dropdown/', views.ajax_dropdown, name='dropdown'),   # HTML fragment for dropdown
    path('unread-count/', views.ajax_unread_count, name='ajax_unread_count'),
    path('mark-all/', views.ajax_mark_all_read, name='mark_all'),   # ajax POST
    path('ajax/mark-as-read/<int:pk>/', views.ajax_mark_as_read, name='ajax_mark_as_read'),
    path('mark-as-read/<int:pk>/', views.MarkAsReadView.as_view(), name='mark_read_single'),
]
