"""Module for users views"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import OperationalError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, UpdateView

from authenticator.constants import LOGIN
from authenticator.utils.mixins import AccessRequiredMixin
from notify.constants import NOTIFY_IS_FOLLOWING
from notify.models import Notification
from users.forms import UpdateUserForm
from users.models import User
from users.constants import (
    USER_DELETED_MSG,
    USER_UPDATED_MSG,
    USER_CONFIRM_DELETE_TEMPLATE,
    USER_ID,
    PROFILE_TEMPLATE,
    PROFILE_EDIT_TEMPLATE, FOLLOWS, FOLLOWING, FOLLOWERS,
    USER_PAGE_TEMPLATE, TARGET_USER,
    GET_USER_PROFILE_URL, FOLLOW, UNFOLLOW, CANT_CREATE_NOTIFICATION, NO_SUCH_USER
)
from users.utils.mixins import UserPageAccessMixin

logger = logging.getLogger(__name__)


class GetProfileView(LoginRequiredMixin, AccessRequiredMixin, DetailView):
    """User profile view"""
    model = User
    pk_url_kwarg = USER_ID
    template_name = PROFILE_TEMPLATE

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        user = self.request.user

        data[FOLLOWING] = user.following.count()
        data[FOLLOWERS] = user.followers.count()

        return data


class UpdateProfileView(LoginRequiredMixin, AccessRequiredMixin, UpdateView):
    """User profile update view"""
    model = User
    pk_url_kwarg = USER_ID
    template_name = PROFILE_EDIT_TEMPLATE
    form_class = UpdateUserForm

    def form_valid(self, form):
        """Creates message about successful update"""
        messages.success(self.request, USER_UPDATED_MSG)
        return super().form_valid(form)

    def get_success_url(self):
        """Get success url with <user.id> parameter"""
        return reverse_lazy(GET_USER_PROFILE_URL, args=[self.request.user.id])


class DeleteProfileView(LoginRequiredMixin, AccessRequiredMixin, DeleteView):
    """View for user deletion"""
    model = User
    pk_url_kwarg = USER_ID
    template_name = USER_CONFIRM_DELETE_TEMPLATE
    success_url = reverse_lazy(LOGIN)

    def form_valid(self, form):
        """Creates message about successful deletion"""
        messages.success(self.request, USER_DELETED_MSG)
        return super().form_valid(form)


class UserPageView(LoginRequiredMixin, UserPageAccessMixin, DetailView):
    """View for displaying user page"""
    model = User
    pk_url_kwarg = USER_ID
    context_object_name = TARGET_USER
    template_name = USER_PAGE_TEMPLATE

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        # Get user object
        user_id = self.kwargs.get("user_id")
        user = User.objects.get(id=user_id)

        # Check if authenticated user is following the target user
        follows = False
        if self.request.user.following.filter(id=user_id).exists():
            follows = True

        data[FOLLOWS] = follows
        data[FOLLOWING] = user.following.count()
        data[FOLLOWERS] = user.followers.count()

        return data


class FollowUserView(LoginRequiredMixin, UserPageAccessMixin, View):
    """
    Represents a feature that allows user follow/unfollow another user
    """

    def get(self, request, user_id):
        """Change status from follow to unfollow and vice-versa

        Args:
            request: request
            user_id: id of user to whom authenticated user wants to follow/unfollow
        """
        # Prefetch following of authenticated user
        user = User.objects.prefetch_related("following").get(id=self.request.user.id)
        try:
            # Get user target object
            user_object = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(NO_SUCH_USER.format(user_id))
            return redirect(GET_USER_PROFILE_URL, user_id=user.id)

        follow_status = FOLLOW
        # Check if authenticated user is following the target user
        if user.following.filter(id=user_id).exists():
            # If following -> unfollow
            user.following.remove(user_object)
        else:
            # If not following -> follow
            user.following.add(user_object)
            follow_status = UNFOLLOW
            try:
                # Create notification
                Notification.create_notification_without_target(actor=user,
                                                                verb=NOTIFY_IS_FOLLOWING,
                                                                recipient=user_object)
            except OperationalError:
                logger.exception(CANT_CREATE_NOTIFICATION.format(user.id, user_object.id))
        response = {
            "follow_status": follow_status,
            "followers_count": user_object.followers.count()
        }

        return JsonResponse(response)
