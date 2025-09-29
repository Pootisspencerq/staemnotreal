# utility home view file (not wired until urls updated)
from django.shortcuts import render
def home(request):
    return render(request, 'home.html')
