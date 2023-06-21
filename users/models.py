"""Module contains users app models"""
import logging
import random
import string

import cloudinary.uploader
from cloudinary.models import CloudinaryField
from django.contrib.auth.base_user import BaseUserManager
from django.db import models, OperationalError
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from reretry import retry
from taggit.managers import TaggableManager
from users.constants import TRIES, DELAY, DEFAULT_EMAIL_PREFIX, DEFAULT_EMAIL_POSTFIX, STRING_LENGTH

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    use_in_migrations = True


    def create_user(self, email=None, password=None, **extra_fields):
        """Creates and saves a User with the given email and password."""
        now = timezone.now()
        if not email:
            # Set a default email for users created through GitHub
            # And if email is not provided
            characters = string.ascii_letters + string.digits
            random_characters = ''.join(random.choice(characters) for _ in range(STRING_LENGTH))
            email = f"{DEFAULT_EMAIL_PREFIX}_{random_characters}@{DEFAULT_EMAIL_POSTFIX}"

        email = self.normalize_email(email)
        user = self.model(email=email,
                          created_at=now, **extra_fields)

        # Check if password is given
        if password:
            user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser):
    """Represents 'users' table in the database"""
    email = models.EmailField(max_length=256, unique=True, db_index=True)
    name = models.CharField(max_length=30, blank=True)
    surname = models.CharField(max_length=30, blank=True)
    bio = models.CharField(max_length=200, blank=True)
    avatar = CloudinaryField("image", folder="avatar", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False,
                                    help_text="Responsible for user email confirmation")
    following = models.ManyToManyField("self", symmetrical=False, related_name="followers")

    objects = UserManager()

    USERNAME_FIELD = "email"

    # Variable for holding current avatar url path.
    # Needed for avatar deletion from cloudinary, if avatar was updated.
    __original_avatar = None

    class Meta:
        db_table = "users"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_avatar = self.avatar

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # Check if original avatar exists and is updated
        if self.__original_avatar and self.avatar != self.__original_avatar:
            # Delete old avatar from cloudinary
            cloudinary.uploader.destroy(self.__original_avatar.public_id, invalidate=True)

        super().save(force_insert, force_update, *args, **kwargs)
        self.__original_avatar = self.avatar

    def __str__(self):
        return self.email

    @classmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def delete_user(cls, user_id: int) -> None:
        """Deletes user

        Args:
            user_id: user id
        """
        User.objects.get(id=user_id).delete()

    def get_full_name(self) -> str:
        """Concatenates name and surname

        Returns:
            Concatenated name and surname of the user
        """
        return f"{self.name} {self.surname}"

    def is_confirmed(self):
        """
        Checks if user is confirmed by looking at field "confirmed" which holds
        information about email confirmation.

        Returns:
             True if email is confirmed, else returns False
        """
        return self.confirmed

    def user_info_provided(self):
        """
        Checks if user data is provided

        Returns:
            True if user data is provided, else False
        """
        return all([self.name, self.surname, self.bio, self.avatar])


class Post(models.Model):
    """Represents 'posts' table in the database"""
    content = models.CharField(max_length=150, default="")
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="+")
    tags = TaggableManager(blank=True)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.content

    @classmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def get_post(cls, post_id: int):
        """Get post by id

        Args:
            post_id: post id
        """
        return Post.objects.prefetch_related("tags", "images", "images__likes").get(id=post_id)

    @classmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def get_posts(cls, user: User = None):
        """Get all posts of specific user

        Args:
            user: User object
        """
        if user:
            return Post.objects.prefetch_related("tags", "images", "user", "likes").filter(user=user)
        return Post.objects.prefetch_related("tags", "images", "user", "likes").all()

    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def get_post_images(self):
        """Get posts images"""
        return self.images.all()


class Image(models.Model):
    """Represents 'images' table in the database"""
    image = CloudinaryField("image", folder="posts", null=True, blank=True)
    post = models.ForeignKey(Post, related_name="images", on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="+")

    class Meta:
        db_table = "images"

    def __str__(self):
        return self.image

    @classmethod
    @retry(exceptions=OperationalError, tries=TRIES, delay=DELAY, logger=logger)
    def create_images(cls, post: Post, images: list):
        """Bulk create images for specific post

        Args:
            post: post object
            images: list of images
        """
        if images:
            for image in images:
                Image.objects.create(post=post, image=image)
