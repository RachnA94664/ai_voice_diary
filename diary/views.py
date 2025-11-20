from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return redirect('login')  # or 'dashboard' if you have that view
    else:
        return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'diary/dashboard.html')


