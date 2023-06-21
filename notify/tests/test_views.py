from django.test import TestCase

from django.urls import reverse

from notify.constants import (
    NOTIFICATIONS_URL, ALL_NOTIFICATIONS_TEMPLATE, NOTIFICATIONS_READ_URL,
    NOTIFICATIONS_DELETE_URL
)
from notify.models import Notification
from test_utils.utils import create_test_user, create_test_users
from users.constants import GET_USER_PROFILE_URL


class NotificationListViewTest(TestCase):
    """Tests for NotificationListView"""

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = create_test_user()

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_url(self):
        """Ensure that user can access notifications url"""
        response = self.client.get(reverse(NOTIFICATIONS_URL))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse(NOTIFICATIONS_URL))
        self.assertTemplateUsed(response, ALL_NOTIFICATIONS_TEMPLATE)


class MarkNotificationAsReadViewTest(TestCase):
    """Test for MarkNotificationAsReadView"""

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1, cls.user2 = create_test_users()

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user1)
        self.notification = Notification.objects.create(actor=self.user1,
                                                        verb="test",
                                                        recipient=self.user2)

    def test_user_can_access_url(self):
        """Ensure that user can access read notification url"""
        response = self.client.get(reverse(NOTIFICATIONS_READ_URL,
                                           args=[self.notification.id]))
        self.assertEqual(response.status_code, 200)

    def test_wrong_notification_id(self):
        """
        Ensure that user is redirected to user profile page
        if wrong notification id"
        """
        response = self.client.get(reverse(NOTIFICATIONS_READ_URL, args=[1]))

        self.assertEqual(response.status_code, 404)


class DeleteNotificationAsReadViewTest(TestCase):
    """Test for DeleteNotificationAsReadView"""

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1, cls.user2 = create_test_users()

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user1)
        self.notification = Notification.objects.create(actor=self.user1,
                                                        verb="test",
                                                        recipient=self.user2)

    def test_user_can_access_url(self):
        """Ensure that user can access delete notification url"""
        response = self.client.get(reverse(NOTIFICATIONS_DELETE_URL, args=[self.notification.id]))
        self.assertEqual(response.status_code, 200)

    def test_wrong_notification_id(self):
        """
        Ensure that user is redirected to user profile page
        if wrong notification id
        """

        response = self.client.get(reverse(NOTIFICATIONS_DELETE_URL, args=[1]))
        self.assertEqual(response.status_code, 404)

