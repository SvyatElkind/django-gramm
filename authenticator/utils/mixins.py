"""Module for mixins used in all apps"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from posts.constants import POST_ID
from users.constants import USER_ID, GET_USER_PROFILE_URL
from users.models import Post


class AccessRequiredMixin(UserPassesTestMixin):
    """Denies access to pages if authenticated user id and user id
    in url parameter does not match in order to prevent
    access to other user pages."""
    def test_func(self):
        """Checks if authenticated user id and user_id in url parameter matches"""
        return self.request.user.id == self.kwargs.get(USER_ID)

    def handle_no_permission(self):
        """Redirects if test fails"""
        return redirect(GET_USER_PROFILE_URL, user_id=self.request.user.id)


class PostAccessMixin(AccessRequiredMixin):
    """Denies access to page if user does not own the post"""
    def test_func(self):
        """Checks if user owns the post"""
        access = super().test_func()

        try:
            # Check, if post exists
            post = Post.objects.get(id=self.kwargs.get(POST_ID))
        except ObjectDoesNotExist:
            return False

        # Check if the post belongs to the user
        post_owner = post.user == self.request.user

        # Return True if user have access and owns the post, else return False
        return access and post_owner


