from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="front_index"),
    path("projects", views.browse_projects, name="front_browse"),
    path("project/", views.project, name="front_project"),
    path("project/<str:name>", views.project, name="front_project"),
    path("transducer/", views.transducer, name="front_transducer"),
    path("transducer/<path:name>", views.transducer, name="front_transducer"),
    path("playground", views.playground, name="front_playground"),
    path("playground/", views.playground, name="front_playground"),
    path("playground/<path:fst>", views.playground, name="front_playground"),
    path("i18n", include("django.conf.urls.i18n")),
]