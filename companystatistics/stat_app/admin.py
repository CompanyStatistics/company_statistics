from django.contrib import admin
from .models import Company, Department, StatTitle, Stat


class DepartmentInline(admin.StackedInline):
    model = Department


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DepartmentInline]


class StatTitleInline(admin.StackedInline):
    model = StatTitle


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'company']
    list_filter = ['company']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [StatTitleInline]


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'amount', 'date', 'created', 'updated']
    list_filter = ['title', 'date']
    search_fields = ['title', 'date']
