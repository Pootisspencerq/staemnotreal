from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('requests/', views.list_requests, name='list_requests'),
    path('send/<int:user_id>/', views.send_request, name='send'),
    path('accept/<int:fr_id>/', views.accept_request, name='accept'),
]
