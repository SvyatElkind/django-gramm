"""Module for signals that triggers changes in db 'notifications' table"""
from typing import Type, Union
import logging

from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from notify.constants import NOTIFY_NEW_POST, ERROR_WHILE_CREATING_POST_NOTIFICATIONS, ERROR_WHILE_DELETING_NOTIFICATION
from notify.models import Notification
from users.models import Post, User, Image

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def new_post_notification(sender: Type[Post], instance: Post, **kwargs):
    """
    Creates notification if new post is created

    Args:
        sender: Post model
        instance: post instance
    """

    # Get user that created post
    actor = User.objects.prefetch_related("followers").filter(id=instance.user.id).first()

    # Create notification
    try:
        Notification.create_notifications(actor=actor,
                                          target_content_type=sender.__name__.lower(),
                                          target_object_id=instance.id,
                                          verb=NOTIFY_NEW_POST,
                                          recipients=actor.followers)
    except OperationalError:
        logger.exception(ERROR_WHILE_CREATING_POST_NOTIFICATIONS.format(instance.id))


@receiver(pre_delete, sender=Image)
@receiver(pre_delete, sender=Post)
def delete_notification(instance: Union[Image, Post], **kwargs):
    """Deletes notification if related target object is deleted

    Args:
        instance: target object being deleted
    """
    try:
        # Delete notification if target object exists in 'notification' table
        Notification.delete_notification_by_target(
            target_content_type=ContentType.objects.get_for_model(instance),
            target_object_id=instance.id
        )
    except OperationalError:
        logger.exception(ERROR_WHILE_DELETING_NOTIFICATION.format(
            ContentType.objects.get_for_model(instance),
            instance.id
        ))
