"""Module for users urls"""
from django.urls import path

from .views import (
    GetProfileView, UpdateProfileView, DeleteProfileView,
    UserPageView, FollowUserView
)

app_name = "users"

urlpatterns = [
    path("profile/<int:user_id>", GetProfileView.as_view(), name="profile"),
    path("profile/<int:user_id>/update", UpdateProfileView.as_view(), name="update"),
    path("profile/<int:user_id>/delete", DeleteProfileView.as_view(), name="delete"),
    path("userpage/<int:user_id>", UserPageView.as_view(), name="userpage"),
    path("userpage/<int:user_id>/follow", FollowUserView.as_view(), name="follow")
]
