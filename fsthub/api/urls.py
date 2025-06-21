from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.routers import DefaultRouter

from .views import (TypesViewset, 
                    LanguageViewset, 
                    ProjectViewSet, 
                    TransducerViewSet)

router = DefaultRouter()
router.register(r'project', ProjectViewSet, basename='api-project')
router.register(r'fst', TransducerViewSet, basename='api-transducer')
router.register(r'fst_type', TypesViewset, basename='api-transducer-type')
router.register(r'fst_language', LanguageViewset, basename='api-transducer-lang')

urlpatterns = [
    #path('call_transducer', CallFstView.as_view(), name='api-call-transducer'),
    #path('filter_transducer', CallFstView.as_view(), name='api-filter-transducer'),
] + router.urls
