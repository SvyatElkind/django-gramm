"""Module for project utilities"""
import logging

import cloudinary.uploader
from cloudinary.exceptions import Error
from django.db.models import QuerySet
from reretry import retry

from users.constants import TRIES, DELAY
from users.models import Image

logger = logging.getLogger(__name__)


@retry(exceptions=Error, tries=TRIES, delay=DELAY, logger=logger)
def delete_image_from_cloudinary(images: QuerySet[Image]):
    """Deletes image from cloudinary

    Args:
        images: list of images that should be deleted
    """
    for image in images:
        result = cloudinary.uploader.destroy(image.image.public_id, invalidate=True)
        if "error" in result:
            logger.warning(f"Cloudinary error: {result['error']['http_code']}, {result['error']['message']}")
