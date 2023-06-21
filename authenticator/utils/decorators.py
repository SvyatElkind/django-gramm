"""Module for decorators"""
from functools import wraps

from django.shortcuts import redirect

from users.constants import GET_USER_PROFILE_URL


def user_not_authenticated(function, redirect_url: str = GET_USER_PROFILE_URL):
    """
    Denies access to specific views by authenticated users

    Args:
        function: Wrapped function
        redirect_url: View name
    """

    @wraps(function)
    def wrapper(request, *args, **kwargs):
        """Checks if user is authenticated"""
        if request.user.is_authenticated:
            return redirect(redirect_url, request.user.id)
        return function(request, *args, **kwargs)

    return wrapper


