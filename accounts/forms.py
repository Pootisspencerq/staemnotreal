from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    links = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'YouTube, Discord, Instagram'})
    )
    class Meta:
        model = Profile
        fields = ['avatar', 'cover', 'display_name', 'bio', 'links', 'theme', 'favorite_color']

