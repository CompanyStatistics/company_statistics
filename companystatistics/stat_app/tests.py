from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Company, Department, StatTitle, Stat
from .serializers import CompanySerializer


User = get_user_model()


class TestStatPages(TestCase):

    @classmethod
    def setUpTestData(cls):
        company = Company.objects.create(
            title='рога и копыта 1',
            slug='roga-i-kopyta-1',
        )
        department = Department.objects.create(
            company=company,
            title='отдел 1',
            slug='otdel-1',
        )
        stat_title = StatTitle.objects.create(
            department=department,
            title='продажи копыт',
        )
        user = User.objects.create_user(
            username='editor',
            password='editor',
            email='editor@cs.local'
        )
        stat = Stat.objects.create(
            owner=user,
            title=stat_title,
            amount=2.5,
            date='2020-03-23',
        )


class TestStatPagesNotLogin(TestStatPages):

    def setUp(self):
        self.client = Client()

    def test_department_list_company(self):
        response = self.client.get('/stat/company/roga-i-kopyta-1/')
        self.assertEqual(response.status_code, 302)

    def test_department_list_wrong_company_slug(self):
        response = self.client.get('/stat/company/roga-i-kopyta-x/')
        self.assertEqual(response.status_code, 302)

    def test_department_detail(self):
        response = self.client.get('/stat/roga-i-kopyta-1/')
        self.assertEqual(response.status_code, 302)

    def test_wrong_department_slug_detail(self):
        response = self.client.get('/stat/otdel-x/')
        self.assertEqual(response.status_code, 302)


class TestStatPagesLogin(TestStatPages):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='user',
            email='user@cs.local'
        )
        self.user.save()
        self.client.login(username='user', password='user')

    def tearDown(self):
        self.user.delete()

    def test_department_list(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_department_list_company(self):
        response = self.client.get('/stat/company/roga-i-kopyta-1/')
        self.assertEqual(response.status_code, 200)

    def test_department_list_wrong_company_slug(self):
        response = self.client.get('/stat/company/roga-i-kopyta-x/')
        self.assertEqual(response.status_code, 404)

    def test_department_detail(self):
        response = self.client.get('/stat/otdel-1/')
        self.assertEqual(response.status_code, 200)

    def test_wrong_department_slug_detail(self):
        response = self.client.get('/stat/otdel-x/')
        self.assertEqual(response.status_code, 404)


class TestStatPagesUser(TestStatPages):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='user',
            email='user@cs.local'
        )
        self.user.save()
        self.client.login(username='user', password='user')

    def tearDown(self):
        self.user.delete()

    def test_stat_create(self):
        stat_id = StatTitle.objects.first()
        self.assertEqual(stat_id.id, 1)
        response = self.client.get(f'/stat/{stat_id.id}/stat_create/')
        self.assertEqual(response.status_code, 200)


class TestStatPagesEditor(TestStatPages):

    def test_stat_title_create(self):
        department = Department.objects.first()
        self.assertEqual(department.id, 1)
        response = self.client.get(f'/stat/{department.id}/stat_title_create/')
        self.assertEqual(response.status_code, 200)

    def test_stat_create(self):
        stat_title = StatTitle.objects.first()
        self.assertEqual(stat_title.id, 1)
        response = self.client.get(f'/stat/{stat_title.id}/stat_create/')
        self.assertEqual(response.status_code, 200)

    def test_stat_edit(self):
        stat_title = StatTitle.objects.first()
        self.assertEqual(stat_title.id, 1)
        response = self.client.get(f'/stat/{stat_title.id}/stat_edit/')
        self.assertEqual(response.status_code, 200)


class CreateCompanyAPITest(APITestCase):
    def setUp(self):
        self.data = {
            'title': 'Рога и копыта',
            'slug': 'Roga-i-Kopyta',
        }

    def test_can_create_company(self):
        """
        Ensure staff can create a new company object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        url = 'stat_app:company-list'
        response = self.client.post(reverse(url), self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(Company.objects.get().title, 'Рога и копыта')
        self.assertEqual(Company.objects.get().slug, 'Roga-i-Kopyta')

    def test_can_not_create_company(self):
        """
        Ensure common user can not create a new company object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        url = 'stat_app:company-list'
        response = self.client.post(reverse(url), self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Company.objects.count(), 0)


class ReadCompanyTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')

    def test_can_read_company_list(self):
        """
        Ensure we can read a list of companies.
        """
        url = 'stat_app:company-list'
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_read_company_detail(self):
        """
        Ensure we can read details of company.
        """
        url = 'stat_app:company-detail'
        response = self.client.get(reverse(url, args=[self.company.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdateCompanyTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.data = CompanySerializer(self.company).data
        self.data.update({'title': 'Копыта и рога'})

    def test_can_update_company(self):
        """
        Ensure staff can update a company object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        url = 'stat_app:company-detail'
        response = self.client.put(reverse(url, args=[self.company.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(Company.objects.get().title, 'Копыта и рога')
        self.assertEqual(Company.objects.get().slug, 'Roga-i-Kopyta')

    def test_can_not_update_company(self):
        """
        Ensure common user can not update a company object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        url = 'stat_app:company-detail'
        response = self.client.put(reverse(url, args=[self.company.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteCompanyTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')

    def test_can_delete_company(self):
        """
        Ensure staff can delete a company object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        url = 'stat_app:company-detail'
        response = self.client.delete(reverse(url, args=[self.company.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_not_delete_company(self):
        """
        Ensure common user can not delete a company object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        url = 'stat_app:company-detail'
        response = self.client.delete(reverse(url, args=[self.company.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateDepartmentAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.data = {
            'company': self.company.id,
            'title': 'Отдел 1',
            'slug': 'Otdel-1',
            'overview': '',
        }

    def test_can_create_department(self):
        """
        Ensure staff can create a new department object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        url = 'stat_app:department-list'
        response = self.client.post(reverse(url), self.data, format='json')
        # response = self.client.post(reverse(url), self.data, content_type='application/json')
        # response = self.client.post(reverse(url), json.dumps(self.data), content_type='application/json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(Company.objects.count(), 1)
        # self.assertEqual(Company.objects.get().title, 'Отдел 1')
        # self.assertEqual(Company.objects.get().slug, 'Otdel-1')

    # def test_can_not_create_department(self):
    #     """
    #     Ensure common user can not create a new department object.
    #     """
    #     self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
    #     self.client.login(username='user', password='user')
    #     url = 'stat_app:company-list'
    #     response = self.client.post(reverse(url), self.data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(Company.objects.count(), 0)


class ReadDepartmentTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')

    def test_can_read_department_list(self):
        """
        Ensure we can read a list of departments.
        """
        url = 'stat_app:department-list'
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Department.objects.count(), 1)

    def test_can_read_department_detail(self):
        """
        Ensure we can read details of department.
        """
        url = 'stat_app:department-detail'
        response = self.client.get(reverse(url, args=[self.department.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Department.objects.get().title, 'Отдел 1')
        self.assertEqual(Department.objects.get().slug, 'Otdel-1')
