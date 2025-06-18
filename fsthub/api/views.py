from django.http import JsonResponse, HttpRequest
from rest_framework import permissions, viewsets, pagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import generics
from rest_framework.reverse import reverse

from .models import FstProject, FstFile
from .serializers import (ProjectSerializer, 
                          ProjectNameSerializer, 
                          FstSerializer,
                          FstNameSerializer)

class LimitedPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProjectsList(generics.ListAPIView):
    queryset = FstProject.objects.all().order_by('directory')
    serializer_class = ProjectNameSerializer
    pagination_class = LimitedPagination
class GetProject(generics.RetrieveAPIView):
    queryset = FstProject.objects.all()
    lookup_field = 'id'
    serializer_class = ProjectSerializer

class FstList(generics.ListAPIView):
    queryset = FstFile.objects.all().order_by('id')
    serializer_class = FstNameSerializer
    pagination_class = LimitedPagination
class GetFst(generics.RetrieveAPIView):
    queryset = FstFile.objects.all()
    lookup_field = 'id'
    serializer_class = FstSerializer

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