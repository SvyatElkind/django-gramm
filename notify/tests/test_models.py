from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from parameterized import parameterized

from notify.constants import NOTIFY_NEW_POST
from notify.models import Notification
from test_utils.utils import create_test_users
from users.models import Post

# Verb used in tests
TEST_VERB = "test"


class NotificationModelTest(TestCase):
    """Class for testing the Notification model"""

    @classmethod
    def setUpTestData(cls):
        """
        Creates two users: one for mostly all test, one for deletion test
        """
        # Create test users
        cls.user1, cls.user2 = create_test_users()

    @parameterized.expand([
        "unread",
        "actor",
        "target_content_type",
        "target_object_id",
        "verb",
        "timestamp",
        "recipient"
    ])
    def test_model_labels(self, field_name: str):
        """Test labels of all fields

        Args:
            field_name: notification model field name
        """
        field_label = Notification._meta.get_field(field_name).verbose_name
        # Replace as field label doesn't have underscore
        field_name = field_name.replace("_", " ")
        self.assertEqual(field_label, field_name)

    def test_create_notifications_without_target(self):
        """Test create_notifications_without_target method"""
        Notification.create_notification_without_target(self.user1, TEST_VERB, self.user2)
        notification = Notification.objects.filter(actor=self.user1).first()
        self.assertEqual(notification.verb, TEST_VERB)
        self.assertEqual(notification.recipient, self.user2)

    def test_create_notification(self):
        """Test create_notification method"""
        post = Post.objects.create(user=self.user2)

        Notification.create_notification(actor=self.user2,
                                         target_content_type=Post.__name__.lower(),
                                         target_object_id=post.id,
                                         verb=NOTIFY_NEW_POST,
                                         recipient=self.user1)

        notification = Notification.objects.filter(actor=self.user2).first()
        self.assertEqual(notification.verb, NOTIFY_NEW_POST)
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.target, post)

    def test_create_notifications(self):
        """Test create_notifications method"""
        # User1 is following user2
        self.user1.following.add(self.user2)
        # User2 creates post
        post = Post.objects.create(user=self.user2)
        # Create notifications for all user2 followers
        Notification.create_notifications(actor=self.user2,
                                          target_content_type=Post.__name__.lower(),
                                          target_object_id=post.id,
                                          verb=NOTIFY_NEW_POST,
                                          recipients=self.user2.followers)
        # Get notification
        notification = Notification.objects.filter(actor=self.user2).first()
        self.assertEqual(notification.verb, NOTIFY_NEW_POST)
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.target, post)

    def test_get_notification(self):
        """Test for get_notification method"""
        # Create notification
        Notification.create_notification_without_target(self.user1, TEST_VERB, self.user2)
        # Get notification
        notifications = Notification.get_notifications(self.user2)
        notification = notifications.first()
        self.assertEqual(notification.verb, TEST_VERB)
        self.assertEqual(notification.actor, self.user1)
        self.assertEqual(notification.recipient, self.user2)

    def test_mark_as_read(self):
        """Test for mark_as_read method"""
        notification = Notification.objects.create(actor=self.user1,
                                                   verb=TEST_VERB,
                                                   recipient=self.user2)
        self.assertTrue(notification.unread)
        # Mark as read
        notification.mark_as_read(self.user2)
        # Refresh 'unread' field
        notification.refresh_from_db(fields=["unread"])
        self.assertFalse(notification.unread)

    def test_delete_notification(self):
        """Test delete_notification method"""

        notification = Notification.objects.create(actor=self.user1,
                                                   verb=TEST_VERB,
                                                   recipient=self.user2)
        notification.delete_notification(self.user2)
        self.assertFalse(Notification.objects.count())
