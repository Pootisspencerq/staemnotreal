from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import ProfileForm
from .models import Profile
@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    return render(request, "accounts/profile.html", {"profile_user": user})

@login_required
def edit_profile_view(request):
    # This ensures a Profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:my_profile")
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, "accounts/edit_profile.html", {"form": form})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect('posts:feed')  # change this to your homepage or feed
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
