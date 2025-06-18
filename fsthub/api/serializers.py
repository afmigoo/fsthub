from .models import FstProject, FstFile
from rest_framework import serializers

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FstProject
        fields = ['id', 'directory', 'author', 'year']
class ProjectNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = FstProject
        fields = ['id', 'directory']

class FstSerializer(serializers.ModelSerializer):
    class Meta:
        model = FstFile
        fields = ['id', 'file_path', 'project']
class FstNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = FstFile
        fields = ['id', 'file_path']
