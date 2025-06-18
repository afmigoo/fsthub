from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="front_index"),
    path("projects", views.browse_projects, name="front_browse"),
    path("project/", views.project, name="front_project"),
    path("project/<int:id>", views.project, name="front_project"),
    path("playground", views.playground, name="front_playground"),
    path("about", views.about, name="front_about"),
    path("i18n", include("django.conf.urls.i18n")),
]