from django.http import JsonResponse, HttpRequest
from rest_framework import permissions, viewsets, pagination
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.throttling import UserRateThrottle
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import generics, status
from rest_framework.reverse import reverse
from django.conf import settings

from hfst_adaptor.call import call_hfst
from .models import FstProject, FstFile
from .serializers import (ProjectSerializer, 
                          ProjectNameSerializer, 
                          FstSerializer,
                          FstNameSerializer,
                          FstCallRequestSerializer)

class LimitedPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class CsrfDisableAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
class FstBurstThrottle(UserRateThrottle):
    scope='fst_burst'
class FstSustainedThrottle(UserRateThrottle):
    scope='fst_sustained'

# Projects
class ProjectsList(generics.ListAPIView):
    queryset = FstProject.objects.all().order_by('directory')
    serializer_class = ProjectNameSerializer
    pagination_class = LimitedPagination
class GetProject(generics.RetrieveAPIView):
    queryset = FstProject.objects.all()
    lookup_field = 'id'
    serializer_class = ProjectSerializer
# Transducers
class FstList(generics.ListAPIView):
    queryset = FstFile.objects.all().order_by('id')
    serializer_class = FstNameSerializer
    #pagination_class = LimitedPagination
class GetFst(generics.RetrieveAPIView):
    queryset = FstFile.objects.all()
    lookup_field = 'id'
    serializer_class = FstSerializer

# TMP
@api_view(['GET'])
def api_fetch_types(request, format=None):
    return Response({'results': [
        {'name': 'transliterator'},
        {'name': 'segmenizer'},
        {'name': 'morph parser'},
        {'name': 'transliteratmorph analyzeror'},
    ]})
@api_view(['GET'])
def api_fetch_langs(request, format=None):
    return Response({'results': [
        {'name': 'Russian'},
        {'name': 'German'},
        {'name': 'Adyghe'},
        {'name': 'Shughni'},
    ]})

class CallFstView(CreateAPIView):
    serializer_class = FstCallRequestSerializer
    throttle_classes = [FstBurstThrottle, FstSustainedThrottle]
    # THIS IS A READ-ONLY POST ENDPOINT
    # and it has to be accessible via third-party apps
    # inputs may be larger than url len limit, so GET cannot be used
    authentication_classes = [CsrfDisableAuthentication]
    def post(self, request, format=None):
        serializer = FstCallRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'output': call_hfst(
                settings.HFST_CONTENT_ROOT / "TEST/sgh_analyze_rulem_word_cyr.hfstol",
                serializer.data['fst_input'].split(),
                oformat=serializer.data['output_format']
            )
        })

# API ROOTS
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'projects': reverse('api-project-root', request=request, format=format),
        'fst': reverse('api-fst-root', request=request, format=format),
    })
@api_view(['GET'])
def project_root(request, format=None):
    return Response({
        'all': reverse('api-all-projects', request=request, format=format),
        'single': reverse('api-get-project', args=[1], request=request, format=format)
    })
@api_view(['GET'])
def fst_root(request, format=None):
    return Response({
        'all': reverse('api-all-fst', request=request, format=format),
        'single': reverse('api-get-fst', args=[1], request=request, format=format)
    })