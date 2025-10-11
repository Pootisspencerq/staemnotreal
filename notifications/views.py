from django.shortcuts import render, redirect
from django.http import HttpResponse


def notification_list(request):
    return render(request, 'notifications/notification_list.html')
