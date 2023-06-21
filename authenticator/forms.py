from authenticator.constants import PASSWORD, CONFIRM_PASSWORD
from users.models import User
from django.contrib.auth.forms import UserCreationForm

from django import forms


# Max length of password
MAX_PASSWORD_LENGTH = 64


class LoginForm(forms.Form):
    """Simple login form"""
    email = forms.EmailField()
    password = forms.CharField(max_length=MAX_PASSWORD_LENGTH, widget=forms.PasswordInput())


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        # Delete fields help text
        for field in [PASSWORD, CONFIRM_PASSWORD]:
            self.fields[field].help_text = None

    class Meta:
        model = User
        fields = ("email",)
