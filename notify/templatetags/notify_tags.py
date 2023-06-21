from typing import Type

from django import template

from notify.models import Notification
from users.models import User

register = template.Library()


@register.simple_tag
def unread_notification(user: Type[User]) -> int:
    """Returns count of authenticated user unread notifications"""
    return Notification.count_unread(user)
