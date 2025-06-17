from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="front_index"),
    path("browse", views.browse, name="front_browse"),
    path("about", views.about, name="front_about"),
    path("i18n", include("django.conf.urls.i18n")),
]