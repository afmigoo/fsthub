from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.routers import DefaultRouter

from .views import (ProjectsList, GetProject, 
                    GetFst, FstList, 
                    api_root, project_root, fst_root,
                    api_fetch_types, api_fetch_langs,
                    CallFstView)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('project', project_root, name='api-project-root'),
    path('project/all', ProjectsList.as_view(), name='api-all-projects'),
    path('project/get/<int:id>', GetProject.as_view(), name='api-get-project'),
    path('fst', fst_root, name='api-fst-root'),
    path('fst/all', FstList.as_view(), name='api-get-all-fst'),
    path('fst/get/<int:id>', GetFst.as_view(), name='api-get-fst'),
    path('fst/types', api_fetch_types, name='api-get-fst-types'),
    path('fst/langs', api_fetch_langs, name='api-get-fst-langs'),
    path('fst/call', CallFstView.as_view(), name='api-call-fst'),
]