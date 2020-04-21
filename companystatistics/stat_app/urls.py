from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

from . import views

app_name = 'stat_app'

router = routers.DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'stat_titles', views.StatTitleViewSet)
router.register(r'stats', views.StatViewSet)

# schema_view = get_schema_view(title='Stat API', description='An API to manage statistics.')

urlpatterns = [
    path('company/<slug:company>/',
         views.DepartmentListView.as_view(),
         name='department_list_company'),
    path('<slug:slug>/',
         views.DepartmentDetailView.as_view(),
         name='department_detail'),
    path('<int:department_id>/stat_title_create/',
         views.stat_title_create,
         name='stat_title_create'),
    path('<int:stat_title_id>/stat_create/',
         views.stat_create,
         name='stat_create'),
    path('<int:stat_id>/stat_edit/',
         views.stat_edit,
         name='stat_edit'),

    path('api/data/', views.get_data, name='api-data'),

    path('api/', include(router.urls)),
    # path('schema/', schema_view),
    # path('docs/', include_docs_urls(title='Stat API'))
]
