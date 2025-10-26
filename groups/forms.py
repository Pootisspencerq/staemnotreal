from django import forms
from .models import Group, GroupPost

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ["content", "file"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }