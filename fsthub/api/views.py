from rest_framework import viewsets, pagination, authentication, throttling
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import status
from django.conf import settings

from hfst_adaptor.call import (
    call_hfst, call_metadata_extractor, call_example_generator, OUTPUT_FORMATS
)
from hfst_adaptor.parse import parse_metadata, parse_example
from hfst_adaptor.exceptions import HfstException
from project_reader import get_projects, get_all_fsts, get_fsts, file_exists, dir_exists
from .models import (
    ProjectMetadata,
    FstType, FstTypeRelation,
    FstLanguage, FstLanguageRelation
)
from .serializers import (
    FstRequest, TypeSerializer, LanguageSerializer, ProjectSerializer,
    FstCallRequestSerializer, FstFilterRequestSerializer, 
    ProjectTransducersRequestSerializer,
    TypeRelationFileSerializer, LangRelationFileSerializer
)

# Pagination
class DefaultPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
# Auth
class CsrfDisableAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        return
# Throttling
class FstBurstThrottle(throttling.UserRateThrottle):
    scope='fst_burst'
class FstSustainedThrottle(throttling.UserRateThrottle):
    scope='fst_sustained'


# Projects
class ProjectViewSet(viewsets.ViewSet):    
    @method_decorator(cache_page(30))
    def list(self, request):
        present_projects = get_projects()
        return Response({
            'results': [{'name': p} for p in present_projects]
        })

    @action(methods=['GET'], detail=False, url_path='transducers', url_name='transducers')
    @method_decorator(cache_page(30))
    def get_transducers(self, request):
        serializer = ProjectTransducersRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not dir_exists(serializer.data['project']):
            return Response({
                'details': 'Project does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        transducers = get_fsts(serializer.data['project'])
        return Response({
            'results': [{'name': p} for p in transducers]
        })

class ProjectMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectMetadata.objects.all()
    serializer_class = ProjectSerializer

# Transducers
class TransducerViewSet(viewsets.ViewSet): 
    @method_decorator(cache_page(30))
    def list(self, request):
        present_fst = get_all_fsts()
        return Response({
            'results': [{'name': p} for p in present_fst]
        })

    @action(methods=['GET'], detail=False)
    @method_decorator(cache_page(60))
    def filter(self, request, format=None):
        serializer = FstFilterRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # If no filters then return everything
        all_fst_files = get_all_fsts()
        if not ('type' in serializer.data or 'lang' in serializer.data):
            return Response({
                'results': [{'name': fst} for fst in all_fst_files]
            })
        # If filters then filter and return
        candidates = set(all_fst_files)
        if 'type' in serializer.data:       
            type_filtered = FstTypeRelation.objects\
                .prefetch_related('type')\
                .filter(type=FstType.objects.get(name=serializer.data['type']))
            serialized = TypeRelationFileSerializer(type_filtered, many=True).data
            candidates.intersection_update(d['fst_file'] for d in serialized)
        if 'lang' in serializer.data:
            lang_filtered = FstLanguageRelation.objects\
                .prefetch_related('language')\
                .filter(language=FstLanguage.objects.get(name=serializer.data['lang']))
            serialized = LangRelationFileSerializer(lang_filtered, many=True).data
            candidates.intersection_update(d['fst_file'] for d in serialized)
        return Response({
            'results': [{'name': n} for n in sorted(candidates)]
        })
        
    @action(methods=['POST'], detail=False,
            authentication_classes=[CsrfDisableAuthentication],
            throttle_classes=[FstBurstThrottle, FstSustainedThrottle])
    def call(self, request, format=None):
        serializer = FstCallRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            output = call_hfst(
                settings.HFST_CONTENT_ROOT / serializer.data['hfst_file'],
                serializer.data['fst_input'].split(),
                oformat=serializer.data['output_format']
            )
            return Response({'output': output.strip()})
        except HfstException as e:
            return Response({
                'details': str(e).replace(str(settings.HFST_CONTENT_ROOT), '.')
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    @action(methods=['GET'], detail=False,
            throttle_classes=[FstBurstThrottle, FstSustainedThrottle])
    @method_decorator(cache_page(60))
    def metadata(self, request, format=None):
        serializer = FstRequest(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not file_exists(serializer.data['hfst_file']):
            return Response({
                'details': 'FST does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            output = call_metadata_extractor(
                settings.HFST_CONTENT_ROOT / serializer.data['hfst_file'],
            )
            parsed = parse_metadata(output)
            return Response({'metadata': parsed})
        except HfstException as e:
            return Response({
                'details': str(e).replace(str(settings.HFST_CONTENT_ROOT), '.')
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @action(methods=['GET'], detail=False,
            throttle_classes=[FstBurstThrottle, FstSustainedThrottle])
    @method_decorator(cache_page(5))
    def example(self, request, format=None):
        serializer = FstRequest(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not file_exists(serializer.data['hfst_file']):
            return Response({
                'details': 'FST does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            output = call_example_generator(
                settings.HFST_CONTENT_ROOT / serializer.data['hfst_file'],
            )
            parsed = parse_example(output)
            return Response({'example': parsed.asdict()})
        except HfstException as e:
            return Response({
                'details': str(e).replace(str(settings.HFST_CONTENT_ROOT), '.')
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @action(methods=['GET'], detail=False)
    @method_decorator(cache_page(300))
    def output_formats(self, request, format=None):
        return Response({'formats': OUTPUT_FORMATS})

# Transducer filters
class TypesViewset(viewsets.ReadOnlyModelViewSet):
    queryset = FstType.objects.all()
    serializer_class = TypeSerializer
class LanguageViewset(viewsets.ReadOnlyModelViewSet):
    queryset = FstLanguage.objects.all()
    serializer_class = LanguageSerializer
