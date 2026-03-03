# NewsPortal/forms.py
from django import forms
from .models import Post, Categories

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'content', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'categories': forms.CheckboxSelectMultiple,
        }