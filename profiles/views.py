from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    return render(request, 'profiles/detail.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', profile.bio)
        profile.save()
        return redirect('profiles:detail', username=request.user.username)
    return render(request, 'profiles/edit.html', {'profile': profile})
