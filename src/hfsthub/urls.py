"""
URL configuration for hfsthub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.urls import path, include

GLOB_PREFIX = os.getenv('GLOB_PREFIX')
GLOB_PREFIX = '' if GLOB_PREFIX is None else GLOB_PREFIX

urlpatterns = [
    path(f'{GLOB_PREFIX}', include('html_pages.urls')),
    path(f'{GLOB_PREFIX}api/', include('api.urls')),
    path(f'{GLOB_PREFIX}admin/', admin.site.urls),
]
