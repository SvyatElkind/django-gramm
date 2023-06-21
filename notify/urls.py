"""Module for notify urls"""
from django.urls import path

from .views import (
    NotificationListView, MarkNotificationAsReadView, DeleteNotificationView
)

app_name = "notify"

urlpatterns = [
    path("all", NotificationListView.as_view(), name="all"),
    path("<int:notification_id>/read", MarkNotificationAsReadView.as_view(), name="read"),
    path("<int:notification_id>/delete", DeleteNotificationView.as_view(), name="delete"),
]