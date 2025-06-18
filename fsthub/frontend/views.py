from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def browse_projects(request):
    return render(request, 'browse_projects.html')
