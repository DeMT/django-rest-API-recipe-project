from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from app.models import Ingredient, Recipe
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

    def test_create_ingredients_successful(self):
        """Test create a new ingredient"""
        payload = {'name': 'cabbage'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_ingredients_invalid(self):
        """Test creating invalid ingredients fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """
        Test filtering ingredients and returning
        those assigned to recipes.
        """
        ingredient1 = Ingredient.objects.create(user=self.user, name='Apples')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Turkey')

        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=10,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredient_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique item"""
        ingredient = Ingredient.objects.create(user=self.user, name='eggs')
        Ingredient.objects.create(user=self.user, name='cheese')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Eggs beneidct',
            time_minutes=30,
            price=12.00
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Coriander eggs on toast',
            time_minutes=20,
            price=5
        )
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
