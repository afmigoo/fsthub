"""
URL configuration for fsthub project.

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
from dotenv import load_dotenv, find_dotenv

from django.contrib import admin
from django.urls import path, include

load_dotenv(find_dotenv('settings.env'))

FSTHUB_PREFIX = os.getenv('FSTHUB_PREFIX', '')
FSTHUB_PREFIX = '' if FSTHUB_PREFIX is None else FSTHUB_PREFIX

urlpatterns = [
    path(f'{FSTHUB_PREFIX}', include('frontend.urls')),
    path(f'{FSTHUB_PREFIX}api/', include('api.urls')),
    path(f'{FSTHUB_PREFIX}admin/', admin.site.urls),
]
