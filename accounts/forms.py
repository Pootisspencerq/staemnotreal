from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "favorite_color"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "favorite_color": forms.TextInput(attrs={"type": "color"}),
        }