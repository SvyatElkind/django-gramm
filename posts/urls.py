"""Module for posts urls"""
from django.urls import path

from .views import (
    GetPostView, CreatePostView, PostListView, DeletePostView,
    UpdatePostView, PostFeedView, SinglePostFeedView,
    PostLikeView, ImageLikeView
)

app_name = "posts"

urlpatterns = [
    path("profile/<int:user_id>/post/create", CreatePostView.as_view(), name="create"),
    path("profile/<int:user_id>/post/<int:post_id>", GetPostView.as_view(), name="post"),
    path("profile/<int:user_id>/post/update/<int:post_id>", UpdatePostView.as_view(), name="update"),
    path("profile/<int:user_id>/post/delete/<int:post_id>", DeletePostView.as_view(), name="delete"),
    path("profile/<int:user_id>/posts/", PostListView.as_view(), name="posts"),
    path("feed/", PostFeedView.as_view(), name="feed"),
    path("feed/<int:post_id>", SinglePostFeedView.as_view(), name="feed_post"),
    path("feed/<int:post_id>/like", PostLikeView.as_view(), name="like"),
    path("feed/<int:post_id>/image_like", ImageLikeView.as_view(), name="image_like"),
]
