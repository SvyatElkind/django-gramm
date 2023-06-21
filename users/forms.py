from django import forms

from users.models import User


class UpdateUserForm(forms.ModelForm):
    """Form for updating users information"""
    class Meta:
        model = User
        fields = ["name", "surname", "bio", "avatar"]
        widgets = {"bio": forms.Textarea()}
