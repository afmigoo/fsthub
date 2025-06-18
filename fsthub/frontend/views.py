from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def browse_projects(request):
    return render(request, 'browse_projects.html')

def playground(request):
    return render(request, 'playground.html')

def project(request, id=None):
    if id is None:
        return redirect('front_browse')
    return render(request, 'project.html', context={
        'project_id': id
    })