from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.routers import DefaultRouter

from .views import (api_fetch_langs, api_fetch_types, TypesViewset, LanguageViewset,
                    CallFstView, ProjectViewSet, TransducerViewSet)

router = DefaultRouter()
router.register(r'project', ProjectViewSet, basename='api-project')
router.register(r'fst', TransducerViewSet, basename='api-transducer')
router.register(r'fst_type', TypesViewset, basename='api-transducer-type')
router.register(r'fst_language', LanguageViewset, basename='api-transducer-lang')

urlpatterns = [
    path('fst/call', CallFstView.as_view(), name='api-call-fst'),
] + router.urls
