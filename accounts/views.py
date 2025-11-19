from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from django.core.mail import EmailMessage
from django.contrib import messages
from .tokens import account_activation_token

User = get_user_model()


# ============================
# 🔹 USER REGISTRATION + EMAIL VERIFICATION
# ============================
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Create inactive user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        # Send activation email
        current_site = get_current_site(request)
        mail_subject = 'Activate your AI Voice Diary account.'
        message = render_to_string('accounts/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })

        email_message = EmailMessage(mail_subject, message, to=[email])
        email_message.send()

        return HttpResponse('Please confirm your email address to complete registration.')

    return render(request, 'accounts/register.html')


# ============================
# 🔹 ACTIVATE ACCOUNT (EMAIL LINK)
# ============================
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for confirming your email. You can now login.')
    else:
        return HttpResponse('Activation link is invalid!')


# ============================
# 🔹 LOGIN VIEW
# ============================
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Change to your actual main page
        else:
            messages.error(request, 'Invalid username or password.')

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


# ============================
# 🔹 LOGOUT VIEW
# ============================
def logout_view(request):
    logout(request)
    return redirect('login')
