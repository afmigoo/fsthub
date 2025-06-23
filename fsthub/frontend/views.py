from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, Http404

from project_reader import dir_exists, file_exists

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def browse_projects(request):
    return render(request, 'browse_projects.html')

def playground(request, fst=None):
    return render(request, 'playground.html', context={
        'selected_fst': fst
    })

def project(request, name=None):
    if name is None:
        return redirect('front_browse')
    if not dir_exists(name):
        raise Http404()
    return render(request, 'project.html', context={
        'project_name': name
    })

def transducer(request, name=None):
    print(type(name))
    if name is None:
        return redirect('front_browse')
    if not file_exists(name):
        raise Http404()
    return render(request, 'fst.html', context={
        'transducer_name': name
    })
