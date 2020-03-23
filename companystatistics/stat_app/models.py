from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType


class Company(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'компания'
        verbose_name_plural = 'компании'
        ordering = ['title']

    def __str__(self):
        return self.title


class Department(models.Model):
    company = models.ForeignKey(Company,
                                related_name='departments',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    overview = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'отдел'
        verbose_name_plural = 'отделы'
        ordering = ['title']

    def __str__(self):
        return self.title


class StatTitle(models.Model):
    department = models.ForeignKey(Department,
                                   related_name='stat_titles',
                                   on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    overview = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'форма'
        verbose_name_plural = 'формы'
        ordering = ['title']

    def __str__(self):
        return self.title


class Stat(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='statistics_created',
                              on_delete=models.DO_NOTHING)
    title = models.ForeignKey(StatTitle,
                              related_name='stats',
                              on_delete=models.CASCADE,)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'данные'
        verbose_name_plural = 'данные'
        ordering = ['date']

    def __str__(self):
        return self.title
