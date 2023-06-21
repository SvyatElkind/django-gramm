from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from authenticator.constants import (
    EMAIL_CONFIRMATION_MSG,
    INVALID_EMAIL_OR_PASSWORD_MSG,
    FURTHER_REGISTRATION_MSG,
    SUCCESSFUL_EMAIL_CONFIRMATION_MSG,
    INVALID_ACTIVATION_LINK_MSG,
    ACTIVATION, LOGIN, INDEX, REGISTER, LOGOUT, PASSWORD, CONFIRM_PASSWORD
)
from authenticator.forms import CustomUserCreationForm, LoginForm
from users.models import User
from test_utils.utils import (
    create_test_user,
    create_unconfirmed_user,
    create_confirmed_user,
    TEST_PASSWORD
)

UIDB64 = "uidb64"
TOKEN = "token"


class IndexViewTest(TestCase):
    """Tests for IndexView"""

    def test_redirection_url(self):
        response = self.client.get(reverse(INDEX))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(LOGIN))


class RegisterViewTest(TestCase):
    """Tests for RegisterView"""

    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_user()

    def test_registration_url_on_get(self):
        """Ensure that user can access registration form"""
        response = self.client.get(reverse(REGISTER))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authenticator/register.html")
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_registration_url_on_post(self):
        """
        Ensure that unauthenticated and unregistered user can post
        registration form
        """
        response = self.client.post(
            reverse(REGISTER),
            data={"email": "test@user.com",
                  PASSWORD: TEST_PASSWORD,
                  CONFIRM_PASSWORD: TEST_PASSWORD}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(LOGIN))
        self.assertTrue(User.objects.filter(email="test@user.com").exists())

    def test_register_user_with_used_email_but_not_confirmed(self):
        response = self.client.post(
            reverse(REGISTER),
            data={"email": "test@user.com",
                  PASSWORD: TEST_PASSWORD,
                  CONFIRM_PASSWORD: TEST_PASSWORD}
        )
        # Get error message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), FURTHER_REGISTRATION_MSG)


    def test_register_user_with_used_and_confirmed_email(self):
        response = self.client.post(
            reverse(REGISTER),
            data={"email": self.user.email,
                  PASSWORD: TEST_PASSWORD,
                  CONFIRM_PASSWORD: TEST_PASSWORD}
        )

        # Get error message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertTrue("User with this Email already exists." in str(messages[0]))


class LoginViewTest(TestCase):
    """Tests for LoginView"""

    @classmethod
    def setUpTestData(cls):
        # Create user
        cls.unconfirmed_user = create_unconfirmed_user()
        cls.confirmed_user = create_confirmed_user()
        cls.user_with_data = create_test_user()

    def test_login_url_on_get(self):
        """Ensure that user can access login form"""
        response = self.client.get(reverse(LOGIN))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authenticator/login.html")
        self.assertIsInstance(response.context["form"], LoginForm)

    def test_login_unconfirmed_user(self):
        """Ensure that unconfirmed user can't login"""
        response = self.client.post(
            reverse(LOGIN),
            data={"email": self.unconfirmed_user.email,
                  "password": TEST_PASSWORD}
        )
        self.assertEqual(response.status_code, 200)
        # Get error message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), EMAIL_CONFIRMATION_MSG)

    def test_login_confirmed_user(self):
        """Ensure that confirmed user can login"""
        response = self.client.post(
            reverse(LOGIN),
            data={"email": self.confirmed_user.email,
                  "password": TEST_PASSWORD},
        )
        self.assertEqual(response.status_code, 302)

    def test_login_user(self):
        """Ensure that user with provided data can access profile page"""
        response = self.client.post(
            reverse(LOGIN),
            data={"email": self.user_with_data.email,
                  "password": TEST_PASSWORD}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/profile/{self.user_with_data.id}")

    def test_login_unregistered_user(self):
        """Ensure unregistered user get error message"""
        response = self.client.post(
            reverse(LOGIN),
            data={"email": "no@email.com",
                  "password": TEST_PASSWORD}
        )
        # Get error message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), INVALID_EMAIL_OR_PASSWORD_MSG)


class LogoutViewTest(TestCase):
    """Tests for LogoutView"""

    def setUp(self):
        # Create and login user
        self.user = create_test_user()
        self.client.login(email=self.user.email, password=TEST_PASSWORD)

    def test_user_is_logged_out(self):
        """Ensure that user has been logged out"""
        response = self.client.get(reverse(LOGOUT))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(LOGIN))
        self.assertFalse("_auth_user_id" in self.client.session)


class UserActivationViewTestCase(TestCase):
    """Tests for UserActivationView"""
    @classmethod
    def setUpTestData(cls):
        # Create unconfirmed user
        cls.user = create_unconfirmed_user()
        # create token and uid
        cls.token = PasswordResetTokenGenerator().make_token(cls.user)
        cls.uid = urlsafe_base64_encode(force_bytes(cls.user.id))

    def test_valid_activation_link(self):
        """Ensure that valid uidb64 and token activates the user"""
        response = self.client.get(reverse(ACTIVATION, kwargs={UIDB64: self.uid, "token": self.token}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(LOGIN))
        # ensure that user is confirmed
        self.assertTrue(User.objects.get(id=self.user.id).confirmed)

        # Get success message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), SUCCESSFUL_EMAIL_CONFIRMATION_MSG)

    def test_invalid_activation_link(self):
        """Ensure that invalid uidb64 and token should not activate the user"""
        response = self.client.get(reverse(ACTIVATION, kwargs={UIDB64: "invalid_uid", TOKEN: self.token}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(LOGIN))
        # ensure that user is not confirmed
        self.assertFalse(get_user_model().objects.get(id=self.user.pk).confirmed)

        response = self.client.get(reverse(ACTIVATION, kwargs={UIDB64: self.uid, TOKEN: "invalid_token"}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(LOGIN))
        # ensure that user is not confirmed
        self.assertFalse(get_user_model().objects.get(id=self.user.pk).confirmed)

        # Get error message
        messages = list(get_messages(response.wsgi_request))
        # ensure there is only one message
        self.assertEqual(len(messages), 1)
        # ensure that message is correct
        self.assertEqual(str(messages[0]), INVALID_ACTIVATION_LINK_MSG)


