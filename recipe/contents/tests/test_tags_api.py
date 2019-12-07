from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from app.models import Tag

from ..serializers import TagSerializer

TAGS_URL = reverse('contents:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags api."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the tags API"""

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@test.com', password='testuser'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieving tags. """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        """Test that return tags are for the user"""

        user2 = get_user_model().objects.create_user(
            email='other@test.com',
            password='otheruser'
        )

        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='comfort_food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertTrue(res.data[0]['name'] == tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag."""
        payload = {'name': 'test_tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_invaild_tag(self):
        """Test creating a invaild tag with payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
