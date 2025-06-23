from rest_framework.routers import DefaultRouter

from .views import (TypesViewset,
                    LanguageViewset, 
                    ProjectViewSet, 
                    ProjectMetadataViewSet,
                    TransducerViewSet)

router = DefaultRouter()
router.register(r'project', ProjectViewSet, basename='api-project')
router.register(r'project_meta', ProjectMetadataViewSet, basename='api-project-meta')
router.register(r'fst', TransducerViewSet, basename='api-transducer')
router.register(r'fst_type', TypesViewset, basename='api-transducer-type')
router.register(r'fst_language', LanguageViewset, basename='api-transducer-lang')

urlpatterns = [
    #path('call_transducer', CallFstView.as_view(), name='api-call-transducer'),
] + router.urls
