from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:user_id>/', views.chat_detail, name='detail'),  # це дає ім'я 'detail'
]
