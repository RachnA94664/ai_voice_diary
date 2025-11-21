from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages

class PremiumMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user
        if user.is_authenticated:
            profile = getattr(user, 'userprofile', None)
            if profile:
                # Example: limit entries for free user
                if not profile.is_premium and profile.entry_count >= 50:
                    if request.path not in [reverse('accounts:upgrade_page'), reverse('accounts:logout')]:
                        messages.error(request, "Entry limit reached. Please upgrade to premium for unlimited entries.")
                        return redirect('accounts:upgrade_page')
        return None
