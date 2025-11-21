from django.http import JsonResponse

def premium_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not check_premium_access(request.user):
            return JsonResponse({'error': 'Premium required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
