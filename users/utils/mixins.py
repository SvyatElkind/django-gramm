"""Module for mixins used in users app"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from posts.constants import POST_ID
from users.constants import USER_ID, GET_USER_PROFILE_URL
from users.models import Post


class UserPageAccessMixin(UserPassesTestMixin):
    """
    Redirects to user profile if authenticated user id is
    equal to user_id parameter in url
    """
    def test_func(self):
        """Checks if authenticated user id and user_id in url parameter does not match"""
        return self.request.user.id != self.kwargs.get(USER_ID)

    def handle_no_permission(self):
        """Redirects if test fails"""
        return redirect(GET_USER_PROFILE_URL, user_id=self.request.user.id)
