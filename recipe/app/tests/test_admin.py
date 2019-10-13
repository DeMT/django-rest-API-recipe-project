from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='superuser@test.com',
            password='superpassword'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@test.com',
            password='tester',
            name='tester name'
        )

    def test_user_exist(self):
        """Test if the test user exist in our admin database."""
        url = reverse('admin:app_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works."""
        url = reverse('admin:app_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the add user page(browser operation) in admin works."""
        url = reverse('admin:app_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
