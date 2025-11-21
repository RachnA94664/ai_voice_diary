from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from accounts.utils import check_premium_access


def premium_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        # If not premium or active trial → block access
        if not check_premium_access(request.user):
            messages.error(
                request,
                "This feature is available for premium users only. Please upgrade your subscription."
            )
            return redirect('accounts:upgrade_page')  # Your original redirect

        # Allowed
        return view_func(request, *args, **kwargs)

    return _wrapped_view
