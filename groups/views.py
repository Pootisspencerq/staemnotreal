from django.shortcuts import render, redirect
from django.http import HttpResponse




def group_list(request):
    return render(request, 'groups/group_list.html')
