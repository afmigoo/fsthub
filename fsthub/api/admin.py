from django.contrib import admin

from .models import (ProjectMetadata, 
                     FstType, FstTypeRelation,
                     FstLanguage, FstLanguageRelation)

admin.site.register(FstLanguageRelation)
admin.site.register(FstTypeRelation)
admin.site.register(FstLanguage)
admin.site.register(FstType)
admin.site.register(ProjectMetadata)
