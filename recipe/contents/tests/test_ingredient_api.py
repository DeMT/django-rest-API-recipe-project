from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from app.models import Ingredient
from ..serializers import IngredientSerializer

INGREDIENT_URL = reverse('contents:ingredient-list')


class PublicIngredientsTestCase(TestCase):
    """Test the publicly available ingredient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testeremail@email.com',
            password='testerpassword'
        )

    def test_login_required(self):
        """Test that login is required to access ingredient endpoints"""
        Ingredient.objects.create(user=self.user, name='Kale')
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsTestCase(TestCase):
    """Test private ingredients enpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testeremail@email.com',
            password='testerpassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            email='unlogin@email.com',
            password='pass'
        )
        ingredient = Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=user2, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], ingredient.name)
