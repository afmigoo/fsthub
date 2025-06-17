from django.http import JsonResponse, HttpRequest
from rest_framework import permissions, viewsets, pagination

from .models import FstProject
from .serializers import FstProjectSerializer

class LimitedPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class FstProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FstProjects to be viewed or edited.
    """
    queryset = FstProject.objects.all().order_by('directory')
    serializer_class = FstProjectSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = LimitedPagination

