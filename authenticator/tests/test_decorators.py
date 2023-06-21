from django.test import TestCase
from django.urls import reverse

from authenticator.constants import LOGIN
from test_utils.utils import create_test_user


class TestDecorators(TestCase):
    """Test for user_not_authenticated decorator"""
    def test_user_not_authenticated_decorator_302(self):
        """Ensure that authenticated user is redirected"""
        self.user = create_test_user()
        self.client.force_login(self.user)
        response = self.client.get(reverse(LOGIN))
        self.assertEqual(response.status_code, 302)
