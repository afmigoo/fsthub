from django.http import JsonResponse, HttpRequest
from rest_framework import permissions, viewsets, pagination
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.throttling import UserRateThrottle
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import generics, status
from rest_framework.reverse import reverse
from django.conf import settings

from hfst_adaptor.call import call_hfst
from hfst_adaptor.exceptions import HfstException
from project_reader import ProjectReader
from .models import ProjectMetadata, FstTypeRelation, FstType, FstLanguage, FstLanguageRelation
from .serializers import (TypeSerializer, LanguageSerializer, ProjectSerializer,
                          FstCallRequestSerializer, FstFilterRequestSerializer, TypeRelationFileSerializer, LangRelationFileSerializer)
# Pagination
class DefaultPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
# Auth
class CsrfDisableAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
# Throttling
class FstBurstThrottle(UserRateThrottle):
    scope='fst_burst'
class FstSustainedThrottle(UserRateThrottle):
    scope='fst_sustained'


# Projects
class ProjectViewSet(viewsets.ViewSet):    
    def list(self, request):
        present_projects = ProjectReader.get_projects()
        return Response({
            'results': [{'name': p} for p in present_projects]
        })
    
    def retrieve(self, request, pk):
        if not ProjectReader.project_exists(pk):
            return Response({
                'detail': f"'{pk}' does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        # TODO check if it exists in DB first
        meta = ProjectMetadata.objects.get(directory=pk)
        return Response({
            'results': meta
        })
        
# Transducers
class TransducerViewSet(viewsets.ViewSet): 
    def list(self, request):
        present_fst = ProjectReader.get_all_fsts()
        return Response({
            'results': [{'name': p} for p in present_fst]
        })
       
    @action(methods=['GET'], detail=False, url_path='filter', url_name='filter')
    def filter(self, request, format=None):
        serializer = FstFilterRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # If no filters then return everything
        all_fst_files = ProjectReader.get_all_fsts()
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
            'results': [{'name': n} for n in candidates]
        })
        
    @action(methods=['POST'], detail=False, url_path='call', url_name='call')
    @throttle_classes([FstBurstThrottle, FstSustainedThrottle])
    @authentication_classes([CsrfDisableAuthentication])
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
            return Response({'output': output})
        except HfstException as e:
            return Response({
                'details': str(e).replace(str(settings.HFST_CONTENT_ROOT), '.')
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# Transducer filters
class TypesViewset(viewsets.ReadOnlyModelViewSet):
    queryset = FstType.objects.all()
    serializer_class = TypeSerializer
class LanguageViewset(viewsets.ReadOnlyModelViewSet):
    queryset = FstLanguage.objects.all()
    serializer_class = LanguageSerializer
