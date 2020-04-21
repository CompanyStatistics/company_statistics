import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Company, Department, StatTitle, Stat
from .serializers import CompanySerializer, DepartmentSerializer, StatTitleSerializer, StatSerializer

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
        self.url = 'stat_app:department-list'

    def test_can_create_department(self):
        """
        Ensure staff can create a new department object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        response = self.client.post(reverse(self.url), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 1)
        self.assertEqual(Department.objects.get().title, 'Отдел 1')
        self.assertEqual(Department.objects.get().slug, 'Otdel-1')

    def test_can_not_create_department(self):
        """
        Ensure common user can not create a new department object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        response = self.client.post(reverse(self.url), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Department.objects.count(), 0)


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


class UpdateDepartmentTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.data = DepartmentSerializer(self.department).data
        self.data.update({'title': 'Отдел 2'})
        self.url = 'stat_app:department-detail'

    def test_can_update_department(self):
        """
        Ensure staff can update a department object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        response = self.client.put(reverse(self.url, args=[self.department.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Department.objects.count(), 1)
        self.assertEqual(Department.objects.get().title, 'Отдел 2')
        self.assertEqual(Department.objects.get().slug, 'Otdel-1')

    def test_can_not_update_department(self):
        """
        Ensure common user can not update a department object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        response = self.client.put(reverse(self.url, args=[self.department.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteDepartmentTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.url = 'stat_app:department-detail'

    def test_can_delete_department(self):
        """
        Ensure staff can delete a department object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        response = self.client.delete(reverse(self.url, args=[self.department.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.count(), 0)

    def test_can_not_delete_department(self):
        """
        Ensure common user can not delete a department object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        response = self.client.delete(reverse(self.url, args=[self.department.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Department.objects.count(), 1)


class CreateStatTitleAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.data = {
            'department': self.department.id,
            'title': 'Продажа рогов',
            'overview': 'Продажа офигенных рогов',
        }
        self.url = 'stat_app:stattitle-list'

    def test_can_create_stat_title(self):
        """
        Ensure staff can create a new stat_title object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        response = self.client.post(reverse(self.url), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StatTitle.objects.count(), 1)
        self.assertEqual(StatTitle.objects.get().title, 'Продажа рогов')
        self.assertEqual(StatTitle.objects.get().overview, 'Продажа офигенных рогов')

    def test_can_not_create_stat_title(self):
        """
        Ensure common user can not create a new stat_title object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        response = self.client.post(reverse(self.url), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(StatTitle.objects.count(), 0)


class ReadStatTitleTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.stat_title = StatTitle.objects.create(
            department=self.department, title='Продажа рогов', overview='Продажа офигенных рогов')

    def test_can_read_stat_title_list(self):
        """
        Ensure we can read a list of stat_titles.
        """
        url = 'stat_app:stattitle-list'
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StatTitle.objects.count(), 1)

    def test_can_read_stat_title_detail(self):
        """
        Ensure we can read details of stat_title.
        """
        url = 'stat_app:stattitle-detail'
        response = self.client.get(reverse(url, args=[self.department.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StatTitle.objects.get().title, 'Продажа рогов')
        self.assertEqual(StatTitle.objects.get().overview, 'Продажа офигенных рогов')


class UpdateStatTitleTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.stat_title = StatTitle.objects.create(
            department=self.department, title='Продажа рогов', overview='Продажа офигенных рогов')
        self.data = StatTitleSerializer(self.stat_title).data
        self.data.update({'title': 'Продажа копыт'})
        self.url = 'stat_app:stattitle-detail'

    def test_can_update_stat_title(self):
        """
        Ensure staff can update a stat_title object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        response = self.client.put(reverse(self.url, args=[self.stat_title.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StatTitle.objects.count(), 1)
        self.assertEqual(StatTitle.objects.get().title, 'Продажа копыт')
        self.assertEqual(StatTitle.objects.get().overview, 'Продажа офигенных рогов')

    def test_can_not_update_stat_title(self):
        """
        Ensure common user can not update a stat_title object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        response = self.client.put(reverse(self.url, args=[self.stat_title.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteStatTitleTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.stat_title = StatTitle.objects.create(
            department=self.department, title='Продажа рогов', overview='Продажа офигенных рогов')
        self.url = 'stat_app:stattitle-detail'

    def test_can_delete_stat_title(self):
        """
        Ensure staff can delete a stat_title object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        response = self.client.delete(reverse(self.url, args=[self.stat_title.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StatTitle.objects.count(), 0)

    def test_can_not_delete_stat_title(self):
        """
        Ensure common user can not delete a stat_title object.
        """
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        response = self.client.delete(reverse(self.url, args=[self.stat_title.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(StatTitle.objects.count(), 1)


class CreateStatAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.stat_title = StatTitle.objects.create(
            department=self.department, title='Продажа рогов', overview='Продажа офигенных рогов')
        self.url = 'stat_app:stat-list'

    def test_can_create_stat(self):
        """
        Ensure staff can create a new stat object.
        """
        user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        data = {
            'owner': user.id,
            'title': self.stat_title.id,
            'amount': 2.5,
            'date': '2020-04-20',
        }
        response = self.client.post(reverse(self.url), data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Stat.objects.count(), 1)
    #     self.assertEqual(Stat.objects.get().amount, data.get('amount'))
    #     self.assertEqual(Stat.objects.get().date, data.get('date'))

    # def test_can_not_create_stat(self):
    #     """
    #     Ensure common user can not create a new stat object.
    #     """
    #     user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
    #     self.client.login(username='user', password='user')
    #     data = {
    #         'owner': user.id,
    #         'title': self.stat_title.id,
    #         'amount': 2.5,
    #         'date': '2020-04-20',
    #     }
    #     response = self.client.post(reverse(self.url), data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(Stat.objects.count(), 0)


class ReadStatTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.stat_title = StatTitle.objects.create(
            department=self.department, title='Продажа рогов', overview='Продажа офигенных рогов')
        self.stat = Stat.objects.create(
            owner=self.user, title=self.stat_title, amount=2.5, date='2020-04-20')

    def test_can_read_stat_list(self):
        """
        Ensure we can read a list of stat.
        """
        url = 'stat_app:stat-list'
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Stat.objects.count(), 1)

    def test_can_read_stat_detail(self):
        """
        Ensure we can read details of stat.
        """
        url = 'stat_app:stat-detail'
        response = self.client.get(reverse(url, args=[self.stat.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Stat.objects.get().amount, 2.5)
        self.assertEqual(Stat.objects.get().date, datetime.date(2020, 4, 20))


class UpdateStatTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.stat_title = StatTitle.objects.create(
            department=self.department, title='Продажа рогов', overview='Продажа офигенных рогов')
        self.url = 'stat_app:stat-detail'

    def test_can_update_stat(self):
        """
        Ensure staff can update a stat object.
        """
        user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        stat = Stat.objects.create(
            owner=user, title=self.stat_title, amount=2.5, date='2020-04-20')
        data = StatSerializer(stat).data
        data.update({'amount': 4.0})
        response = self.client.put(reverse(self.url, args=[stat.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Stat.objects.count(), 1)
        self.assertEqual(Stat.objects.get().amount, 4.0)

    def test_can_not_update_stat(self):
        """
        Ensure common user can not update a stat object.
        """
        user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        stat = Stat.objects.create(
            owner=user, title=self.stat_title, amount=2.5, date='2020-04-20')
        data = StatSerializer(stat).data
        data.update({'amount': 4.0})
        response = self.client.put(reverse(self.url, args=[stat.id]), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteStatTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Рога и копыта', slug='Roga-i-Kopyta')
        self.department = Department.objects.create(company=self.company, title='Отдел 1', slug='Otdel-1')
        self.stat_title = StatTitle.objects.create(
            department=self.department, title='Продажа рогов', overview='Продажа офигенных рогов')
        self.url = 'stat_app:stat-detail'

    def test_can_delete_stat(self):
        """
        Ensure staff can delete a stat object.
        """
        user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=True)
        self.client.login(username='user', password='user')
        stat = Stat.objects.create(
            owner=user, title=self.stat_title, amount=2.5, date='2020-04-20')
        response = self.client.delete(reverse(self.url, args=[stat.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Stat.objects.count(), 0)

    def test_can_not_delete_stat(self):
        """
        Ensure common user can not delete a stat object.
        """
        user = User.objects.create_user('user', 'user@cs.local', 'user', is_staff=False)
        self.client.login(username='user', password='user')
        stat = Stat.objects.create(
            owner=user, title=self.stat_title, amount=2.5, date='2020-04-20')
        response = self.client.delete(reverse(self.url, args=[stat.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Stat.objects.count(), 1)
