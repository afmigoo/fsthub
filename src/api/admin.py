from django.contrib import admin

from .models import FstProject, FstFile

admin.site.register(FstProject)
admin.site.register(FstFile)
