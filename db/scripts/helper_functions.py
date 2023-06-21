"""Module contains functions related to database"""
from typing import Union

from django.shortcuts import get_object_or_404

from users.models import Post, Image, User


def like_unlike_object(instance: Union[Post, Image],
                       user: User) -> bool:
    """Like/unlike object

    Allows authenticated user like/unlike specific object

    Args:
        instance: Either image or post instance
        user: authenticated user that likes/unlikes object

    Returns:
        True if object is liked, else return False
    """
    liked = False
    # Check if user liked the target object yet
    if instance.likes.filter(id=user.id).exists():
        # if target object is liked -> unlike
        instance.likes.remove(user)
    else:
        # if target object is unliked -> like
        instance.likes.add(user)
        liked = True

    return liked
