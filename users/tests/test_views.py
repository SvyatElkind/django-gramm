from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from test_utils.utils import create_test_users, create_test_user_without_data, TEST_PASSWORD, create_test_user
from users.constants import USER_UPDATED_MSG, USER_DELETED_MSG
from users.models import User


class GetProfileViewTest(TestCase):
    """Tests for GetProfileView"""

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user1, cls.user2 = create_test_users()
        cls.user_no_data = create_test_user_without_data()

    def setUp(self):

        # Login user for all tests
        self.client.force_login(self.user1)

    def test_status_code_when_user_can_access_profile_url(self):
        """Ensure that status code is 200 when user access his profile page"""
        response = self.client.get(f"/profile/{self.user1.id}")
        self.assertEqual(response.status_code, 200)

    def test_when_user_try_access_other_user_profile_url(self):
        """Ensure that user can't access other user profile page"""
        response = self.client.get(f"/profile/{self.user2.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/profile/{self.user1.id}")

    def test_when_no_user_data_provided(self):
        """Ensure, that user is redirected to update page if no user data provided"""
        self.client.login(email=self.user_no_data.email,
                          password=TEST_PASSWORD)
        response = self.client.get(f"/profile/{self.user_no_data.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/profile/{self.user_no_data.id}/update")

    def test_view_url_by_name(self):
        """Test url by name"""
        response = self.client.get(reverse("users:profile", args=[self.user1.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test url used template"""
        response = self.client.get(reverse("users:profile", args=[self.user1.id]))
        self.assertTemplateUsed(response, "users/profile.html")


class UpdateProfileViewTest(TestCase):
    """Tests for UpdateProfileView"""
    @classmethod
    def setUpTestData(cls):

        cls.user = create_test_user()

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_update_profile_view(self):
        """Ensure that user can access update profile view"""
        response = self.client.get(f"/profile/{self.user.id}/update")
        self.assertEqual(response.status_code, 200)

    def test_user_can_update_profile(self):
        """Ensure that user can update profile"""
        response = self.client.post(
            f"/profile/{self.user.id}/update",
            data={"name": "Lana",
                  "surname": "La",
                  "bio": "Test bio"}
        )

        # Get success message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), USER_UPDATED_MSG)

        # refresh user fields
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.user.name, "Lana")
        self.assertEqual(self.user.surname, "La")
        self.assertEqual(self.user.bio, "Test bio")


class DeleteProfileViewTest(TestCase):
    """Tests for DeleteProfileView"""
    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_user()

    def setUp(self):
        # Login user for all tests
        self.client.force_login(self.user)

    def test_user_can_access_delete_profile_view(self):
        """Ensure user can access delete profile view"""
        response = self.client.get(f"/profile/{self.user.id}/delete")
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_profile(self):
        """Ensure that user can delete profile"""
        response = self.client.post(f"/profile/{self.user.id}/delete")

        # Get success message
        messages = list(get_messages(response.wsgi_request))

        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), USER_DELETED_MSG)
        # ensure status code is correct
        self.assertEqual(response.status_code, 302)
        # ensure that user is deleted
        self.assertFalse(User.objects.filter(id=self.user.id).exists())


class UserPageViewTest(TestCase):
    """Tests for UserPageProfileView"""

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user1, cls.user2 = create_test_users()

    def setUp(self):

        # Login user for all tests
        self.client.force_login(self.user1)

    def test_status_code_when_user_access_his_userpage_url(self):
        """Ensure that status code is 302 when user try to access his user page"""
        response = self.client.get(f"/userpage/{self.user1.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/profile/{self.user1.id}")

    def test_status_code_when_user_try_access_other_user_userpage_url(self):
        """Ensure that user can access other user userpage"""
        response = self.client.get(f"/userpage/{self.user2.id}")
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        """Test url by name"""
        response = self.client.get(reverse("users:userpage", args=[self.user2.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test url used template"""
        response = self.client.get(reverse("users:userpage", args=[self.user2.id]))
        self.assertTemplateUsed(response, "users/user_page.html")


class FollowUserViewTest(TestCase):
    """Tests for FollowUserView"""

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user1, cls.user2 = create_test_users()

    def setUp(self):

        # Login user for all tests
        self.client.force_login(self.user1)

    def test_when_auth_user_follows_and_unfollows_the_other_user(self):
        """Test when authenticated user follows and unfollows the other user"""

        # User1 is following user2
        response = self.client.get(f"/userpage/{self.user2.id}/follow")

        self.assertTrue(self.user1.following.filter(id=self.user2.id).exists())
        # User2 has user1 in his followers
        self.assertTrue(self.user2.followers.filter(id=self.user1.id).exists())

        # User1 is unfollowing user2
        response = self.client.get(f"/userpage/{self.user2.id}/follow")

        self.assertFalse(self.user1.following.filter(id=self.user2.id).exists())
        # User2 has not user1 in his followers
        self.assertFalse(self.user2.followers.filter(id=self.user1.id).exists())
