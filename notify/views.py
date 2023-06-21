"""Views for notifications"""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView

from notify.models import Notification
from notify.constants import ALL_NOTIFICATIONS_TEMPLATE, NOTIFICATIONS_URL
from users.constants import GET_USER_PROFILE_URL


class NotificationListView(LoginRequiredMixin, ListView):
    """View for authenticated user notifications"""
    model = Notification
    paginate_by = settings.PAGINATE_BY
    context_object_name = "notifications"
    template_name = ALL_NOTIFICATIONS_TEMPLATE

    def get_queryset(self):
        """Get authenticated user notifications"""
        notifications = Notification.get_notifications(self.request.user)
        return notifications


class MarkNotificationAsReadView(LoginRequiredMixin, View):
    """View for mark specific notification as read """

    def get(self, request, notification_id):
        """Marks notification as read"""
        user = self.request.user

        notification = get_object_or_404(Notification, id=notification_id)
        notification.mark_as_read(user)

        response = {
            "notification_read": True,
            "unread_notification_count": Notification.count_unread(user)
        }

        return JsonResponse(response)


class DeleteNotificationView(LoginRequiredMixin, View):
    """View for specific notification deletion"""

    def get(self, request, notification_id):
        """Deletes specific notification"""
        user = self.request.user

        notification = get_object_or_404(Notification, id=notification_id)
        notification.delete_notification(user)

        response = {
            "notification_count": Notification.get_notifications(user).count(),
            "unread_notification_count": Notification.count_unread(user)
        }

        return JsonResponse(response)
