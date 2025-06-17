from django.http import JsonResponse

def endpoint(request):
    return JsonResponse({'foo': 'bar', 'bar': 5})
