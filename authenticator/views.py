"""Module contains views for user authentication"""

from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.db import OperationalError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.views import View
import logging

from reretry import retry

from users.constants import GET_USER_PROFILE_URL, TRIES, DELAY
from .constants import (
    REGISTER, LOGIN,
    EMAIL_CONFIRMATION_MSG, INVALID_EMAIL_OR_PASSWORD_MSG,
    SUCCESSFUL_EMAIL_CONFIRMATION_MSG, INVALID_ACTIVATION_LINK_MSG, BAD_LOGIN, LOGIN_TEMPLATE, REGISTER_TEMPLATE
)
from authenticator.utils.decorators import user_not_authenticated
from .forms import CustomUserCreationForm, LoginForm
from authenticator.utils.utils import send_confirmation_email

logger = logging.getLogger(__name__)


class IndexView(View):
    """
    Used solely for user redirection to login page
    """
    def get(self, request):
        """Redirects user to login page"""
        return redirect(LOGIN)


@method_decorator(user_not_authenticated, name="dispatch")
class RegisterView(View):
    """
    User registration view
    """
    def get(self, request):
        """Returns template with registration form"""
        form = CustomUserCreationForm()
        return render(request, REGISTER_TEMPLATE, {"form": form})

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY)
    def post(self, request):
        """
        Creates user if form is valid, else redirects
        to registration page with error message(s).
        """
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user and send confirmation email
            user = form.save()
            send_confirmation_email(user, request)
            return redirect(LOGIN)
        else:
            # Collect error messages to be displayed in template
            for message in form.errors.values():
                messages.error(request, message)
            return redirect(REGISTER)


@method_decorator(user_not_authenticated, name="dispatch")
class LoginView(View):
    """
    View for user login
    """
    def get(self, request):
        """Returns template with login form"""
        form = LoginForm()
        return render(request, LOGIN_TEMPLATE, {"form": form})

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY)
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            # Check if credentials are valid or not
            user = authenticate(request, email=email, password=password)

            if user:
                if not user.is_confirmed():
                    # If user did not confirmed his or her email
                    messages.error(request, EMAIL_CONFIRMATION_MSG)
                    return render(request, LOGIN_TEMPLATE, {'form': form})

                try:
                    # If email confirmed then log the user in and redirect to the profile page.
                    login(request, user)
                    return redirect(GET_USER_PROFILE_URL, user_id=user.id)
                except SuspiciousOperation:
                    logger.exception(BAD_LOGIN)
                    return redirect(LOGIN)

            else:
                messages.error(request, INVALID_EMAIL_OR_PASSWORD_MSG)
                return redirect(LOGIN)


@method_decorator(login_required, name="dispatch")
class LogoutView(View):
    """
    View for user logout
    """
    def get(self, request):
        """Logout user from application"""
        logout(request)
        return redirect(LOGIN)


class UserActivationView(View):
    """
    View for user activation
    """

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY)
    def get(self, request, uidb64, token):
        """Checks user id and token and confirms user"""
        # Get User model
        User = get_user_model()
        try:
            # Decode uidb64 and get user
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except DjangoUnicodeDecodeError:
            logger.exception(INVALID_ACTIVATION_LINK_MSG)
            # If no user with decoded uid found
            user = None

        if user and PasswordResetTokenGenerator().check_token(user, token):
            # If user and generated token is valid, confirm user.
            user.confirmed = True
            user.save()

            messages.success(request, SUCCESSFUL_EMAIL_CONFIRMATION_MSG)
            return redirect(LOGIN)
        else:
            # If user or generated token is invalid, inform user.
            messages.error(request, INVALID_ACTIVATION_LINK_MSG)
            return redirect(LOGIN)
