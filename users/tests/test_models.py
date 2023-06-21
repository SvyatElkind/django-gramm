from django.test import TestCase

from parameterized import parameterized

from test_utils.utils import TEST_PASSWORD, create_test_user_without_data, create_test_user, create_test_users
from users.models import User, Post, Image


class UserModelTest(TestCase):
    """Class for testing the User model"""

    @classmethod
    def setUpTestData(cls):
        """
        Creates two users: one for mostly all test, one for deletion test
        """
        cls.user = create_test_user_without_data()
        cls.user_for_deletion = create_test_user()

    @parameterized.expand([
        "email",
        "name",
        "surname",
        "bio",
        "avatar",
        "confirmed",
        "created_at"
    ])
    def test_model_labels(self, field_name: str):
        """Test labels of all fields

        Args:
            field_name: user model field name
        """
        field_label = self.user._meta.get_field(field_name).verbose_name
        # Replace as field label doesn't have underscore
        field_name = field_name.replace("_", " ")
        self.assertEqual(field_label, field_name)

    @parameterized.expand([
        ("email", 256),
        ("name", 30),
        ("surname", 30),
        ("bio", 200)
    ])
    def test_labels_max_length(self, field_name: str, length: int):
        """Test max length of the fields that have this parameter

        Args:
            field_name: field name with max length parameter
            length: value of max length parameter
        """
        max_length = self.user._meta.get_field(field_name).max_length
        self.assertEqual(max_length, length)

    def test_confirmed_field_help_text(self):
        """Test help text of confirmed field"""
        help_text = self.user._meta.get_field("confirmed").help_text
        self.assertEqual(help_text, "Responsible for user email confirmation")

    def test_object_name(self):
        """Test object.__str__ return value"""
        object_name = self.user.email
        self.assertEqual(str(self.user), object_name)

    def test_get_full_name_method(self):
        """Test get_full_name method"""
        full_name = f"{self.user.name} {self.user.surname}"
        self.assertEqual(self.user.get_full_name(), full_name)

    def test_is_confirmed(self):
        """Test is_confirmed method"""
        self.assertEqual(self.user.is_confirmed(), self.user.confirmed)

    def test_user_info_provided_false(self):
        """Test user_info_provided method"""
        self.assertFalse(self.user.user_info_provided())

    def test_user_info_provided_true(self):
        """Test user_info_provided method"""
        self.user.bio = "About Me"
        self.user.avatar = "/path/to/avatar"
        self.assertTrue(self.user.user_info_provided())

    def test_delete_user(self):
        User.delete_user(user_id=self.user_for_deletion.id)
        self.assertEqual(User.objects.count(), 1)


class PostModelTest(TestCase):
    """Class for testing the Post model"""

    @classmethod
    def setUpTestData(cls):
        """Create user and post"""
        cls.user, cls.user2 = create_test_users()
        cls.post = Post.objects.create(content="First post",
                                       user=cls.user)
        cls.post2 = Post.objects.create(content="Second post",
                                        user=cls.user2)

    @parameterized.expand([
        "content",
        "user",
        "likes"
    ])
    def test_model_labels(self, field_name: str):
        """Test labels of all fields

        Except tags field, where verbose name is set by TaggableManager
        and created_at field as it's verbose name is without underscore

        Args:
            field_name: post model field name
        """
        field_label = self.post._meta.get_field(field_name).verbose_name
        self.assertEqual(field_label, field_name)

    def test_created_at_field_label(self):
        """Test for label created_at field"""
        field_label = self.post._meta.get_field("created_at").verbose_name
        self.assertEqual(field_label, "created at")

    def test_content_field_default_parameter(self):
        """Test content default parameter"""
        default_value = self.post._meta.get_field("content").default
        self.assertEqual(default_value, "")

    def test_content_field_max_length(self):
        """Test content default parameter"""
        length = self.post._meta.get_field("content").max_length
        self.assertEqual(length, 150)

    def test_object_name(self):
        """Test object.__str__ return value"""
        self.assertEqual(str(self.post), self.post.content)

    def test_get_post(self):
        """Test get_post method"""
        post = Post.get_post(post_id=self.post.id)
        self.assertEqual(self.post, post)

    def test_get_posts_with_specific_user_argument(self):
        """Test get_posts method"""
        posts = Post.get_posts(user=self.user)
        self.assertEqual(posts.count(), 1)

    def test_get_posts_without_specific_user_argument(self):
        """Test get_posts method"""
        posts = Post.get_posts()
        self.assertEqual(posts.count(), 2)


class ImageModelTest(TestCase):
    """Class for testing the Image model"""

    @classmethod
    def setUpTestData(cls):
        """Create user and post"""
        cls.user = create_test_user()
        cls.post = Post.objects.create(content="First post",
                                       user=cls.user)

        cls.image = Image.objects.create(post=cls.post, image="test.jpg")

    @parameterized.expand([
        "image",
        "post"
    ])
    def test_model_labels(self, field_name: str):
        """Test labels of all fields

        Args:
            field_name: image model field name
        """
        field_label = self.image._meta.get_field(field_name).verbose_name
        self.assertEqual(field_label, field_name)

    def test_object_name(self):
        self.assertEqual(str(self.image), self.image.image)

    def test_create_image(self):
        images = ["first.jpg", "second.jpg"]
        Image.create_images(self.post, images=images)
        self.assertEqual(self.post.images.count(), 3)


