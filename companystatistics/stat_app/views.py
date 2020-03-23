from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic.base import TemplateResponseMixin, View

from .forms import StatForm, StatTitleForm
from .models import Department, Company, StatTitle, Stat


class DepartmentListView(LoginRequiredMixin, TemplateResponseMixin, View):
    model = Department
    template_name = 'stat_app/department/list.html'

    def get(self, request, company=None):
        companies = Company.objects.annotate(
            total_departments=Count('departments'))
        departments = Department.objects.annotate(
            total_stat_titles=Count('stat_titles'))
        if company:
            company = get_object_or_404(Company, slug=company)
            departments = departments.filter(company=company)

        return self.render_to_response({'companies': companies,
                                        'company': company,
                                        'departments': departments})


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'stat_app/department/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DepartmentDetailView,
                        self).get_context_data(**kwargs)
        stat_titles = StatTitle.objects.filter(department=self.object)
        stats = Stat.objects.all()
        context['stat_titles'] = stat_titles
        context['stats'] = stats

        return context


def stat_create(request, stat_title_id):
    stat_title = StatTitle.objects.filter(id=stat_title_id).first()
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
