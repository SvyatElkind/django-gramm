"""Module contains notify app models"""
import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, OperationalError
from django.db.models import QuerySet
from reretry import retry

from notify.constants import (
    NOTIFICATION_DOES_NOT_EXIST, TARGET_CONTENT_TYPE, TARGET_OBJECT_ID,
    VERB_MAX_LENGTH
)
from users.constants import TRIES, DELAY
from users.models import User

logger = logging.getLogger(__name__)


class Notification(models.Model):
    """
    Represents 'notifications' table in database
    """

    unread = models.BooleanField(default=True, db_index=True)

    actor = models.ForeignKey(User,
                              blank=False,
                              on_delete=models.CASCADE)

    target_content_type = models.ForeignKey(ContentType,
                                            blank=True,
                                            null=True,
                                            on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey(TARGET_CONTENT_TYPE, TARGET_OBJECT_ID)

    verb = models.CharField(max_length=VERB_MAX_LENGTH)
    timestamp = models.DateTimeField(auto_now_add=True)

    recipient = models.ForeignKey(User,
                                  blank=False,
                                  related_name="notifications",
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ("-timestamp",)
        index_together = ("recipient", "unread")

    @staticmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def create_notifications(
            actor: User,
            target_content_type: str,
            target_object_id: int,
            verb: str,
            recipients: QuerySet):
        """
        Creates multiple notifications

        Args:
            actor: the authenticated user that performed the activity
            target_content_type: type of the object to which the activity was performed
            target_object_id: id of objet to which the activity was performed
            verb: phrase that identifies the action of the activity
            recipients: queryset with users that should be notified
        """
        if recipients:
            # If there is at least one user in queryset
            for single_recipient in recipients.all():
                Notification.create_notification(
                    actor=actor,
                    target_content_type=target_content_type,
                    target_object_id=target_object_id,
                    verb=verb,
                    recipient=single_recipient
                )

    @staticmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def create_notification(
            actor: User,
            target_content_type: str,
            target_object_id: int,
            verb: str,
            recipient: User):
        """
        Creates notification

        Args:
           actor: the authenticated user that performed the activity
           target_content_type: type of the object to which the activity was performed
           target_object_id: id of objet to which the activity was performed
           verb: phrase that identifies the action of the activity
           recipient: user that should be notified
        """
        Notification.objects.create(
            actor=actor,
            target_content_type=ContentType.objects.get(app_label="users",
                                                        model=target_content_type),
            target_object_id=target_object_id,
            verb=verb,
            recipient=recipient)

    @staticmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def create_notification_without_target(actor: User,
                                           verb: str,
                                           recipient: User):
        """
        Creates notification without target object

        Args:
           actor: the authenticated user that performed the activity
           verb: phrase that identifies the action of the activity
           recipient: user that should be notified
        """
        Notification.objects.create(actor=actor,
                                    verb=verb,
                                    recipient=recipient)

    @staticmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def get_notifications(user: User) -> QuerySet:
        """Returns authenticated user notifications

        Args:
            user: authenticated user

        Returns:
            QuerySet with notifications
        """
        return Notification.objects.prefetch_related("actor").filter(recipient=user)

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def mark_as_read(self, user: User):
        """Marks specific notification as read

        Args:
            user: authenticated user
        """
        if self.recipient == user and self.unread:
            self.unread = False
            self.save()

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def delete_notification(self, user: User):
        """Deletes specific notification

        Args:
            user: authenticated user
        """
        if self.recipient == user:
            self.delete()

    @staticmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def delete_notification_by_target(target_content_type: str, target_object_id: int):
        """Deletes notifications related to specific target object"""
        Notification.objects.filter(
            target_content_type=target_content_type,
            target_object_id=target_object_id
        ).delete()

    @staticmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def count_unread(user):
        """Counts unread notifications of authenticated user

        Returns:
            Count of unread notifications
        """
        return Notification.objects.filter(recipient=user, unread=True).count()
