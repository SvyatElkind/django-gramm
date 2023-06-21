from django import forms

from users.constants import CONTENT_FIELD, TAGS_FIELD
from users.models import Post


class CreatePostForm(forms.ModelForm):
    """Form for creating post"""
    images = forms.ImageField(required=False,
                              widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Post
        fields = [CONTENT_FIELD, TAGS_FIELD]
        widgets = {CONTENT_FIELD: forms.Textarea()}


class UpdatePostForm(forms.ModelForm):
    """Form for updating post"""
    class Meta:
        model = Post
        fields = [CONTENT_FIELD, TAGS_FIELD]
        widgets = {CONTENT_FIELD: forms.Textarea()}
