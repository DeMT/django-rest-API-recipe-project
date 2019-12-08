from django.test import TestCase
from django.contrib.auth import get_user_model

from .. import models


def sample_user(email='tester@gmail.com', password='testerpassowrd'):
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """test creating a new user with email and verify
            that user exist in database."""
        email = 'tester@gmail.com'
        password = 'testerpassowrd'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_nomalized(self):
        """test a new user's email is nomalized"""
        email = 'tester@gmail.Com'
        password = 'testerpassowrd'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, 'tester@gmail.com')

    def test_new_user_invaild_email(self):
        """test creating user with no email raise error"""
        with self.assertRaises(ValueError):
            password = 'testerpassowrd'
            get_user_model().objects.create_user(
                email=None,
                password=password
            )

    def test_create_superuser(self):
        """Test if a super user got created correctly."""
        email = 'testersuper@gmail.Com'
        password = 'testersuperpassowrd'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )
        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.is_staff, True)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)
