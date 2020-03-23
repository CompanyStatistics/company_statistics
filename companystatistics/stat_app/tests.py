from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from .models import Company, Department, StatTitle, Stat


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
        user = get_user_model().objects.create_user(
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
        self.user = get_user_model().objects.create_user(
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
        self.user = get_user_model().objects.create_user(
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
