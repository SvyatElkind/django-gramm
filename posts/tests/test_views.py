from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from posts.constants import (
    POST_LIST_TEMPLATE,
    CREATE_POST_TEMPLATE,
    POST_CREATED_MSG,
    SINGLE_POST_TEMPLATE,
    UPDATE_POST_TEMPLATE,
    POST_DELETED_MSG,
    POST_CONFIRM_DELETE_TEMPLATE,
    FEED_POST_TEMPLATE,
    FEED_POST_PREVIEW_TEMPLATE, POSTS_FEED_URL
)
from users.models import Post, Image
from test_utils.utils import create_test_user, create_test_users, create_posts

# User ID that is not used in test cases
OTHER_USER_ID = 9
OTHER_USERS_POST_ID = 9
# Posts per page
POSTS_PER_PAGE = 10
# Number of posts to be created by user
NUMBER_OF_POSTS = 11


class PostListViewTest(TestCase):
    """Tests for PostListView"""
    @classmethod
    def setUpTestData(cls):

        # Create test user
        cls.user = create_test_user()
        # Create posts
        create_posts(NUMBER_OF_POSTS, cls.user)

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_url(self):
        """Ensure that user can access posts url"""
        response = self.client.get(reverse(POSTS_FEED_URL, args=[self.user.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse(POSTS_FEED_URL, args=[self.user.id]))
        self.assertTemplateUsed(response, POST_LIST_TEMPLATE)


class CreatePostViewTest(TestCase):
    """Tests for CreatePostView"""
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = create_test_user()

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_url(self):
        """Ensure that user can access posts url"""
        response = self.client.get(reverse("posts:create", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse("posts:create", args=[self.user.id]))
        self.assertTemplateUsed(response, CREATE_POST_TEMPLATE)

    def test_user_can_create_post(self):
        """Ensure that user can create post"""
        response = self.client.post(
            f"/profile/{self.user.id}/post/create",
            kwargs={"pk": self.user.id},
            data={"content": "Test Post",
                  "tags": "first, second"}
        )

        # Get success message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), POST_CREATED_MSG)

        # ensure status code is correct
        self.assertEqual(response.status_code, 302)

        # ensure post is created
        self.assertTrue(Post.objects.filter(user=self.user).exists())
        # ensure user has only one post
        self.assertEqual(Post.objects.filter(user=self.user).count(), 1)


class GetPostViewTest(TestCase):
    """Tests for GetPostView"""
    @classmethod
    def setUpTestData(cls):
        # Create test user and post
        cls.user = create_test_user()
        cls.post = Post.objects.create(user=cls.user, content="My post")

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_url(self):
        """Ensure that user can access posts url"""
        response = self.client.get(reverse("posts:post", args=[self.user.id, self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse("posts:post", args=[self.user.id, self.post.id]))
        self.assertTemplateUsed(response, SINGLE_POST_TEMPLATE)

    def test_post_is_correct(self):
        """Ensure that post in response is correct"""
        response = self.client.get(reverse("posts:post", args=[self.user.id, self.post.id]))
        self.assertEqual(response.context["post"], self.post)


class UpdatePostViewTest(TestCase):
    """Tests for UpdatePostView"""
    @classmethod
    def setUpTestData(cls):
        # Create test user and post
        cls.user = create_test_user()
        cls.post = Post.objects.create(user=cls.user, content="My post")

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_url(self):
        """Ensure that user can access update post url"""
        response = self.client.get(reverse("posts:update", args=[self.user.id, self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse("posts:update", args=[self.user.id, self.post.id]))
        self.assertTemplateUsed(response, UPDATE_POST_TEMPLATE)

    def test_user_can_update_profile(self):
        """Ensure that user can update post"""
        response = self.client.post(
            f"/profile/{self.user.id}/post/update/{self.post.id}",
            data={"content": "New post"}
        )
        # refresh post fields
        self.post.refresh_from_db()

        # ensure status code is correct
        self.assertEqual(response.status_code, 302)
        # ensure content field is updated
        self.assertEqual(self.post.content, "New post")


class DeletePostViewTest(TestCase):
    """Tests for DeletePostView"""
    @classmethod
    def setUpTestData(cls):
        # Create test user and post
        cls.user = create_test_user()
        cls.post = Post.objects.create(user=cls.user, content="My post")

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_url(self):
        """Ensure that user can access delete post url"""
        response = self.client.get(reverse("posts:delete", args=[self.user.id, self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse("posts:delete", args=[self.user.id, self.post.id]))
        self.assertTemplateUsed(response, POST_CONFIRM_DELETE_TEMPLATE)

    def test_user_can_delete_post(self):
        """Ensure that user can delete post"""
        response = self.client.post(
            f"/profile/{self.user.id}/post/delete/{self.post.id}",
        )

        # Get success message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), POST_DELETED_MSG)

        # ensure status code is correct
        self.assertEqual(response.status_code, 302)
        # ensure that post is deleted
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())


class PostFeedViewTest(TestCase):
    """Tests for PostFeedView"""
    @classmethod
    def setUpTestData(cls):
        # Create test users and posts
        cls.user1, cls.user2 = create_test_users()

        # Create posts for user1
        create_posts(6, cls.user1)

        # Create posts for user2
        create_posts(5, cls.user2)
    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user1)


    def test_user_can_access_url(self):
        """Ensure that user can access delete post url"""
        response = self.client.get(reverse("posts:feed"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse("posts:feed"))
        self.assertTemplateUsed(response, FEED_POST_TEMPLATE)


class SinglePostFeedViewTest(TestCase):
    """Tests for PostFeedView"""
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1, cls.user2 = create_test_users()

        cls.post = Post.objects.create(user=cls.user2, content="My post")

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user1)

    def test_user_can_access_url(self):
        """Ensure that user can access delete post url"""
        response = self.client.get(reverse("posts:feed_post", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Ensure that url uses correct template"""
        response = self.client.get(reverse("posts:feed_post", args=[self.post.id]))
        self.assertTemplateUsed(response, FEED_POST_PREVIEW_TEMPLATE)

    def test_post_likes(self):
        """
        Ensure that post don't have likes and user1 did not like user2 post
        """
        response = self.client.get(reverse("posts:feed_post", args=[self.post.id]))
        self.assertEqual(response.context["post_likes_count"], 0)
        self.assertEqual(response.context["post_liked"], False)


class PostLikeViewTest(TestCase):
    """Tests for PostFeedView"""
    @classmethod
    def setUpTestData(cls):
        # Create test users and posts
        cls.user1, cls.user2 = create_test_users()

        cls.post = Post.objects.create(user=cls.user2, content="My post")

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user1)

    def test_user_can_like_post(self):
        """Ensure that user can like the post"""
        response = self.client.get(reverse("posts:like", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.likes.count(), 1)
        self.assertTrue(self.user1 in self.post.likes.all())

        # Ensure that user can unlike the post
        response = self.client.get(reverse("posts:like", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.likes.count(), 0)


class ImageLikeViewTest(TestCase):
    """Tests for PostFeedView"""
    @classmethod
    def setUpTestData(cls):
        # Create test users and posts
        cls.user1 = create_test_user()

        cls.post = Post.objects.create(user=cls.user1, content="My post")

        cls.image = Image.objects.create(post=cls.post, image="test.jpg")

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user1)

    def test_user_can_like_image(self):
        """Ensure that user can like the image"""
        response = self.client.get(f"/feed/{self.post.id}/image_like?image_id={self.image.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.image.likes.count(), 1)
        self.assertTrue(self.user1 in self.image.likes.all())

        # Ensure that user can unlike the post
        response = self.client.get(f"/feed/{self.post.id}/image_like?image_id={self.image.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.image.likes.count(), 0)
        self.assertFalse(self.user1 in self.post.likes.all())

    def test_if_bad_query_parameter(self):
        """Ensure that image is not liked if bad parameter"""
        response = self.client.get(f"/feed/{self.post.id}/image_like?image_id=test")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.image.likes.count(), 0)
        self.assertFalse(self.user1 in self.image.likes.all())

    def test_if_image_does_not_exist(self):
        """Ensure that rendering if image does not exist to single post page"""
        response = self.client.get(f"/feed/{self.post.id}/image_like?image_id={self.image.id+1}")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.image.likes.count(), 0)
        self.assertFalse(self.user1 in self.image.likes.all())
