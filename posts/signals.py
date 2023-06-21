from typing import Type

import cloudinary.uploader
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from users.models import Post
from utils.project_utils import delete_image_from_cloudinary


@receiver(pre_delete, sender=Post)
def delete_images(sender: Type[Post], instance: Post, **kwargs):
    """
    Delete images from cloudinary before post deletion

    Args:
        sender: Post model
        instance: post instance
    """
    images = instance.get_post_images()
    delete_image_from_cloudinary(images)
