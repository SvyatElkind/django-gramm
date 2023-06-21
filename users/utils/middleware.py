"""Module for users Middleware"""
from django.contrib import messages
from django.shortcuts import redirect

from users.constants import UPDATE_USER_PROFILE_URL, FILL_IN_ALL_FIELDS


class NoUserDataMiddleware:
    """
    Middleware ensures that authenticated user provides his or her data
    (name, surname, bio and avatar) in order to access to full functionality.

    If no data or not all data are provided, user will be redirected to update page.

    However, user can logout and delete own profile.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Allow authenticated user logout and delete his/her profile
        if request.path == "/logout/" or request.path == f"/profile/{request.user.id}/delete":
            return self.get_response(request)

        if not request.user.user_info_provided() and request.path != f"/profile/{request.user.id}/update":
            # Ask user to fill all fields and redirect to update page
            messages.error(request, FILL_IN_ALL_FIELDS)
            return redirect(UPDATE_USER_PROFILE_URL, request.user.id)

        response = self.get_response(request)

        return response
