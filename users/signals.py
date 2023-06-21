from typing import Type

import cloudinary.uploader
from django.db.models.signals import pre_delete
from django.dispatch import receiver


from users.models import User


@receiver(pre_delete, sender=User)
def delete_avatar(sender: Type[User], instance: User, **kwargs):
    """
    Delete avatar from cloudinary before user deletion

    Args:
        sender: User model
        instance: user instance
    """

    cloudinary.uploader.destroy(instance.avatar.public_id, invalidate=True)