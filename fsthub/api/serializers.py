from .models import FstProject
from rest_framework import serializers

class FstProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FstProject
        fields = ['directory', 'author', 'year']

