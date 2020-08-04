from django.test import TestCase
from django.test import Client

from .models import CSUser


class TestCaseAdminLogin(TestCase):
    """Test case with client and login as admin function."""
    admin_password = 'admin'

    @classmethod
    def setUpTestData(cls):
        CSUser.objects.create_superuser(username='admin', email='admin@cs.local', password=cls.admin_password)

    def setUp(self):
        self.client = Client()
        self.login()

    def login(self):
        """Login as admin."""
        success = self.client.login(username='admin', password=self.admin_password)
        self.assertTrue(success)
        response = self.client.get('/admin/', follow=True)
        self.assertEqual(response.status_code, 200)
        return response


class TestAdminPages(TestCaseAdminLogin):

    def test_admin_homepage(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


class TestCaseUserLogin(TestCase):
    user_password = 'user'

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        CSUser.objects.create_user(username='user', email='user@cs.local', password=cls.user_password,
                                   # first_name='First', last_name='Last'
                                   )

    def setUp(self):
        self.client = Client()
        self.login()

    def login(self):
        """Login as user."""
        success = self.client.login(username='user', password=self.user_password)
        self.assertTrue(success)
        response = self.client.get('', follow=True)
        self.assertEqual(response.status_code, 200)
        return response


class TestUserPagesLogin(TestCaseUserLogin):

    def test_user_profile(self):
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, 200)

    def test_user_edit(self):
        response = self.client.get('/auth/edit/')
        self.assertEqual(response.status_code, 200)


class TestUserLogout(TestCaseUserLogin):

    def logout(self):
        """Logout as user."""
        success = self.client.logout()
        self.assertTrue(success)
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/auth/edit/')
        self.assertEqual(response.status_code, 302)


class TestUserProperties(TestCaseUserLogin):

    def test_object_name(self):
        user = CSUser.objects.get(id=1)
        self.assertEquals('user', str(user))

    def test_object_email(self):
        user = CSUser.objects.get(id=1)
        self.assertEquals('user@cs.local', str(user.email))

    def test_first_name_label(self):
        user = CSUser.objects.get(id=1)
        field_label = user._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'имя')

    def test_object_first_name(self):
        user = CSUser.objects.get(id=1)
        self.assertEquals('', user.first_name)


class TestUserPagesNotLogin(TestCase):

    def setUp(self):
        self.client = Client()

    def test_user_profile(self):
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, 302)

    def test_user_edit(self):
        response = self.client.get('/auth/edit/')
        self.assertEqual(response.status_code, 302)
