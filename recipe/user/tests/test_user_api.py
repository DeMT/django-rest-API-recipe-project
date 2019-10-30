from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserTest(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_craete_valid_user_success(self):
        """Test creating user with vaild payload is successful."""
        payload = {
            'email': 'testuser@test.com',
            'password': 'testuser',
            'name': 'doomedOneWillBeDestory'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists falls."""
        payload = {'email': 'testuser@test.com',
                   'password': 'testuser', 'name': 'aleady'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password need to be more than 5 characters"""
        payload = {'email': 'testuser@test.com',
                   'password': 'test', 'name': 'tooshort'}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that the token is create for user"""
        payload = {'email': 'testuser@test.com',
                   'password': 'test', 'name': 'tooshort'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invaild_credentials(self):
        """Test that the token is invaild if invaild data is provided."""
        payload = {'email': 'testuser@test.com',
                   'password': 'test'}
        create_user(**payload)
        invaild_data = {'email': 'testuser@test.com', 'password': '12345abc'}
        res = self.client.post(TOKEN_URL, invaild_data)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesnt exists."""
        payload = {'email': 'testuser@test.com',
                   'password': 'test'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """Missing required data when create token"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that unauthorized user can't get access to  user/me endpoint"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """ Test API that required authentication"""

    def setUp(self):
        self.client = APIClient()
        payload = {'email': 'testuser@test.com',
                   'password': 'test', 'name': 'name'}
        self.user = create_user(**payload)

        self.client.force_authenticate(self.user)

    def test_retrieve_user_profile_success(self):
        """Test retrieving profile for logged in user """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data, {'name': self.user.name, 'email': self.user.email})

    def test_post_me_not_allowed(self):
        """Test that post is not allowed at user/me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'name': 'newname',
            'password': 'newpassword'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
