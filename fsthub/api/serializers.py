from .models import FstProject, FstFile
from rest_framework import serializers
from rest_framework.validators import ValidationError
from pathlib import Path
from django.conf import settings

from hfst_adaptor.call import OUTPUT_FORMATS

# Models
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

# Requests
class FstCallRequestSerializer(serializers.Serializer):
    fst_input = serializers.CharField(required=True, allow_blank=False, max_length=10_000)
    hfst_file = serializers.CharField(required=True, allow_blank=False, max_length=500)
    output_format = serializers.ChoiceField(OUTPUT_FORMATS, required=False, default=OUTPUT_FORMATS[0])

    def validate(self, data):
        if '..' in data['hfst_file']:
            raise ValidationError(f'hfst_file \'{data["hfst_file"]}\' is invalid.')
        path_obj = settings.HFST_CONTENT_ROOT.joinpath(data['hfst_file'])
        if not (path_obj.is_file() and path_obj.exists()):
            raise ValidationError(f'hfst_file \'{data["hfst_file"]}\' does not exist.')
        return data
