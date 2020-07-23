from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic.base import TemplateResponseMixin, View
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .forms import StatForm, StatTitleForm
from .models import Department, Company, StatTitle, Stat
from .serializers import CompanySerializer, DepartmentSerializer, StatTitleSerializer, StatSerializer


class DepartmentListView(LoginRequiredMixin, TemplateResponseMixin, View):
    model = Department
    template_name = 'stat_app/department/list.html'

    def get(self, request, company_slug: Optional[str] = None):
        companies = _annotate_companies()
        company = _get_company(company_slug)
        departments = _get_departments(company)
        context = {'companies': companies,
                   'company': company,
                   'departments': departments}
        return self.render_to_response(context)


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'stat_app/department/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DepartmentDetailView,
                        self).get_context_data(**kwargs)
        context['stat_titles'] = _get_stat_titles(department=self.object)
        context['stats'] = _get_all_stats()
        return context


def stat_create(request, stat_title_id):
    stat_title = _get_stat_title(stat_title_id)
    if request.method == "POST":
        form = StatForm(request.POST)
        if form.is_valid():
            stat = form.save(commit=False)
            stat.owner = request.user
            stat.title = stat_title
            stat.save()
            return redirect('department_list')
    else:
        form = StatForm()
    context = {
        'form': form,
        'stat_title': stat_title.title,
    }
    return render(request, 'stat_app/stat/form.html', context)


def stat_edit(request, stat_id):
    stat = get_object_or_404(Stat, id=stat_id)
    if request.method == "POST":
        form = StatForm(request.POST, instance=stat)
        if form.is_valid():
            stat = form.save(commit=False)
            stat.owner = request.user
            stat.save()
            return redirect('department_list')
    else:
        form = StatForm(instance=stat)
    context = {
        'form': form,
        'stat_title': stat.title,
        'object': stat,
    }
    return render(request, 'stat_app/stat/form.html', context)


def stat_title_create(request, department_id=None):
    if department_id:
        department = Department.objects.filter(id=department_id).first()
        if request.method == "POST":
            form = StatTitleForm(request.POST)
            if form.is_valid():
                stat_title = form.save(commit=False)
                stat_title.department = department
                stat_title.save()
                return redirect('stat_app:department_detail', department.slug)
        else:
            form = StatTitleForm()
        context = {
            'form': form,
            'department': department,
        }
        return render(request, 'stat_app/stat_title/form.html', context)


def get_data(request, *args, **kwargs):
    stats = Stat.objects.all()

    stats_dict = {str(StatTitle.objects.filter(title=stat.title).first().id): {'default': [], 'labels': []} for stat in
                  stats}

    for stat in stats:
        stats_dict[str(StatTitle.objects.filter(title=stat.title).first().id)]['default'].append(float(stat.amount))
        stats_dict[str(StatTitle.objects.filter(title=stat.title).first().id)]['labels'].append(str(stat.date))
    data = {
        'stats_dict': stats_dict,
    }

    return JsonResponse(data)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows companies to be viewed or edited.
    """
    queryset = Company.objects.all().order_by('title')
    serializer_class = CompanySerializer

    # permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows departments to be viewed or edited.
    """
    queryset = Department.objects.all().order_by('title')
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    # def perform_create(self, serializer):
    #     company_id = self.kwargs.get('company_id')
    #     company = get_object_or_404(Company, id=company_id)
    #     serializer.save(company=company)

    def create(self, request, *args, **kwargs):
        try:
            item = request.data
            if not (item.get('title') and item.get('slug')):
                raise AttributeError
            company_id = item.get('company')
            company = get_object_or_404(Company, id=company_id)
            item['company'] = company
            department = Department.objects.create(**item)
            return Response(status=status.HTTP_201_CREATED)
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            query_dict = request.data
            item = dict(query_dict.items())
            department_id = kwargs.get('pk')
            if not department_id:
                raise AttributeError
            Department.objects.filter(id=department_id).update(**item)
            return Response(status=status.HTTP_200_OK)
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StatTitleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stat_titles to be viewed or edited.
    """
    queryset = StatTitle.objects.all().order_by('title')
    serializer_class = StatTitleSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            item = request.data
            if not item.get('title'):
                raise AttributeError
            department_id = item.get('department')
            department = get_object_or_404(Department, id=department_id)
            item['department'] = department
            StatTitle.objects.create(**item)
            return Response(status=status.HTTP_201_CREATED)
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            query_dict = request.data
            item = dict(query_dict.items())
            id_ = kwargs.get('pk')
            if not id_:
                raise AttributeError
            StatTitle.objects.filter(id=id_).update(**item)
            return Response(status=status.HTTP_200_OK)
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stats to be viewed or edited.
    """
    queryset = Stat.objects.all().order_by('-date')
    serializer_class = StatSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        try:
            item = request.data
            if not (item.get('amount') and item.get('date')):
                raise AttributeError
            owner_id = item.get('owner')
            stat_title_id = item.get('title')
            owner = get_object_or_404(get_user_model(), id=owner_id)
            title = get_object_or_404(StatTitle, id=stat_title_id)
            item['owner'] = owner
            item['title'] = title
            Stat.objects.create(**item)
            return Response(status=status.HTTP_201_CREATED)
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            query_dict = request.data
            item = dict(query_dict.items())
            id_ = kwargs.get('pk')
            if not id_:
                raise AttributeError
            Stat.objects.filter(id=id_).update(**item)
            return Response(status=status.HTTP_200_OK)
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


def _annotate_companies() -> QuerySet:
    """Annotate companies with the number of departments"""
    return Company.objects.annotate(total_departments=Count('departments'))


def _annotate_departments() -> QuerySet:
    """Annotate departments with the number of forms (stat_titles)"""
    return Department.objects.annotate(total_stat_titles=Count('stat_titles'))


def _get_company(company_slug: Optional[str]) -> Optional[Company]:
    """Get company by slug from database"""
    if company_slug:
        return get_object_or_404(Company, slug=company_slug)
    else:
        return None


def _get_departments(company: Optional[Company]) -> QuerySet:
    """Get departments of the company from database"""
    departments = _annotate_departments()
    if company:
        return departments.filter(company=company)
    else:
        return departments


def _get_stat_titles(department: Department) -> QuerySet:
    """Get stat_titles of the department from database"""
    return StatTitle.objects.filter(department=department)


def _get_all_stats() -> QuerySet:
    """Get all stats from database"""
    return Stat.objects.all()


def _get_stat_title(stat_title_id: int) -> StatTitle:
    """Get stat_title by id from database"""
    return StatTitle.objects.get(id=stat_title_id)
