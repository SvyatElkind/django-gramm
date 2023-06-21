"""Module for posts views"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import OperationalError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView, DeleteView, DetailView, CreateView, UpdateView
)
from django.conf import settings
from reretry import retry

from authenticator.utils.mixins import AccessRequiredMixin, PostAccessMixin
from db.scripts.helper_functions import like_unlike_object
from notify.constants import (
    NOTIFY_LIKE_IMAGE, NOTIFY_LIKE_POST, ERROR_WHILE_CREATING_LIKE_OBJECT_NOTIFICATION
)
from notify.models import Notification
from posts.constants import (
    POST_DELETED_MSG, POSTS_FEED_URL, POST_ID,
    POST_CONFIRM_DELETE_TEMPLATE, POST_LIST_TEMPLATE,
    SINGLE_POST_TEMPLATE, POST_CREATED_MSG,
    CREATE_POST_TEMPLATE, UPDATE_POST_TEMPLATE,
    FEED_POST_TEMPLATE, FEED_POST_PREVIEW_TEMPLATE, SINGLE_POST_FEED_URL
)
from posts.forms import CreatePostForm, UpdatePostForm
from users.constants import TRIES, DELAY
from users.models import Image, Post

logger = logging.getLogger(__name__)


class PostListView(LoginRequiredMixin, AccessRequiredMixin, ListView):
    """View for displaying user posts"""
    model = Post
    paginate_by = settings.PAGINATE_BY
    context_object_name = "posts"
    template_name = POST_LIST_TEMPLATE

    def get_queryset(self):
        """Get user posts"""
        return Post.get_posts(self.request.user)


class CreatePostView(LoginRequiredMixin, AccessRequiredMixin, CreateView):
    """View for post creation"""
    model = Post
    form_class = CreatePostForm
    template_name = CREATE_POST_TEMPLATE

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Add images after creating post
        Image.create_images(self.object,
                            self.request.FILES.getlist("images"))

        messages.success(self.request, POST_CREATED_MSG)
        return response

    def get_success_url(self):
        """Get success url with <user.id> parameter"""
        return reverse_lazy(POSTS_FEED_URL, args=[self.request.user.id])


class GetPostView(LoginRequiredMixin, PostAccessMixin, DetailView):
    """Single post view"""
    model = Post
    pk_url_kwarg = POST_ID
    template_name = SINGLE_POST_TEMPLATE

    def get_object(self):
        return Post.get_post(self.kwargs.get("post_id"))


class UpdatePostView(LoginRequiredMixin, PostAccessMixin, UpdateView):
    """Update post view"""
    model = Post
    pk_url_kwarg = POST_ID
    template_name = UPDATE_POST_TEMPLATE
    form_class = UpdatePostForm

    def get_success_url(self):
        """Get success url with <user.id> parameter"""
        return reverse_lazy(POSTS_FEED_URL, args=[self.request.user.id])


class DeletePostView(LoginRequiredMixin, PostAccessMixin, DeleteView):
    """View for post deletion"""
    model = Post
    pk_url_kwarg = POST_ID
    template_name = POST_CONFIRM_DELETE_TEMPLATE

    def form_valid(self, form):
        """Creates message about successful deletion"""
        messages.success(self.request, POST_DELETED_MSG)
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        """Get success url with <user.id> parameter"""
        return reverse_lazy(POSTS_FEED_URL, args=[self.request.user.id])


class PostFeedView(LoginRequiredMixin, ListView):
    """View for displaying all posts in the feed"""
    model = Post
    paginate_by = settings.PAGINATE_BY
    context_object_name = "posts"
    template_name = FEED_POST_TEMPLATE

    def get_queryset(self):
        """Get user posts"""
        return Post.get_posts()


class SinglePostFeedView(LoginRequiredMixin, DetailView):
    """Feed single post view"""
    model = Post
    pk_url_kwarg = POST_ID
    template_name = FEED_POST_PREVIEW_TEMPLATE

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        post = Post.get_post(self.kwargs.get("post_id"))
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        data["post_likes_count"] = post.likes.count()
        data["post_liked"] = liked
        return data


class PostLikeView(LoginRequiredMixin, View):
    """Represents a feature that allows users to like or unlike a post"""

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def get(self, request, post_id):
        user = request.user
        post = Post.objects.prefetch_related("likes", "user").get(id=post_id)

        # Like/unlike post
        liked = like_unlike_object(post, user)

        if liked:
            # Create notification only if other user post is liked
            if user != post.user:
                try:
                    Notification.create_notification(actor=user,
                                                     target_content_type=Post.__name__.lower(),
                                                     target_object_id=post.id,
                                                     verb=NOTIFY_LIKE_POST,
                                                     recipient=post.user)
                except OperationalError:
                    logger.exception(ERROR_WHILE_CREATING_LIKE_OBJECT_NOTIFICATION.format(
                        Post.__name__.lower(),
                        post.id
                    ))

        response = {
            "likes_count": post.likes.count(),
            "liked": liked
        }

        return JsonResponse(response)


class ImageLikeView(LoginRequiredMixin, View):
    """
    Represents a feature that allows users to like or unlike
    a single image from the post
    """

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def get(self, request, post_id):
        user = request.user

        # Get image_id value
        try:
            image_id = int(request.GET["image_id"])
        except (ValueError, KeyError) as error:
            # Log exception and redirect to the post
            logger.error(error)
            return redirect(SINGLE_POST_FEED_URL, post_id=post_id)

        try:
            image = Image.objects.prefetch_related("likes", "post__user").get(id=image_id)
        except Image.DoesNotExist:
            return redirect(SINGLE_POST_FEED_URL, post_id=post_id)

        # Like/unlike image
        liked = like_unlike_object(image, user)

        if liked:
            # Create notification only if other user image is liked
            if user != image.post.user:
                try:
                    Notification.create_notification(actor=user,
                                                     target_content_type=Image.__name__.lower(),
                                                     target_object_id=image.id,
                                                     verb=NOTIFY_LIKE_IMAGE,
                                                     recipient=image.post.user)
                except OperationalError:
                    logger.exception(ERROR_WHILE_CREATING_LIKE_OBJECT_NOTIFICATION.format(
                        Image.__name__.lower(),
                        image.id
                    ))

        response = {
            "likes_count": image.likes.count(),
            "liked": liked
        }

        return JsonResponse(response)
