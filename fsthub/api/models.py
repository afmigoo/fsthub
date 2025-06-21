from django.db import models
from django.db.models import constraints
from django.core.exceptions import ValidationError
from django.conf import settings

from pathlib import Path

class ProjectMetadata(models.Model):
    directory = models.CharField(max_length=100,primary_key=True)
    author = models.CharField(max_length=200,blank=True,default='')
    year = models.IntegerField(blank=True,null=True)
    description = models.CharField(max_length=1000,blank=True,null=True)

    def validate_dir_exists(self):
        path: Path = settings.HFST_CONTENT_ROOT / self.directory
        if not (path.is_dir() and path.exists()):
            raise ValidationError("Directory '{dir}' does not exist!".format(
                dir=path,
                root=settings.HFST_CONTENT_ROOT
            ))
    def clean(self):
        super().clean()
        self.validate_dir_exists()

    def __repr__(self):
        return f'<{type(self).__name__}: {self.directory}>'
    def __str__(self):
        return self.directory

# Fst filters
class FstFilter(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500,blank=True,default='')

    class Meta:
        abstract = True

    def __repr__(self):
        return f'<{type(self).__name__} {self.name}>'
    def __str__(self):
        return self.name
class FstType(FstFilter):
    pass
class FstLanguage(FstFilter):
    pass
    
class FstFilterRelation(models.Model):
    fst_file = models.CharField(max_length=100)

    class Meta:
        abstract = True
    def validate_file_exists(self):
        path = settings.HFST_CONTENT_ROOT / self.fst_file
        if not (path.is_file() and path.exists()):
            raise ValidationError("File '{file}' does not exist!".format(
                file=path,
                root=settings.HFST_CONTENT_ROOT
            ))
    def clean(self):
        super().clean()
        self.validate_file_exists()
    def __repr__(self):
        return f'<{type(self).__name__} {str(self)}>'

class FstTypeRelation(FstFilterRelation):
    type = models.ForeignKey(FstType, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['fst_file'],
                name='unique_fst_file_for_type'
            ),
        ]
    def __str__(self):
        return f'{self.type.name} : {self.fst_file}'
    
class FstLanguageRelation(FstFilterRelation):
    language = models.ForeignKey(FstLanguage, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['fst_file'],
                name='unique_fst_file_for_lang'
            ),
        ]
    def __str__(self):
        return f'{self.language.name} : {self.fst_file}'
    