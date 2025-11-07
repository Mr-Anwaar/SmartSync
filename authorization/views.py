from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test


# Create your views here.

def anonymous_required(function=None, redirect_url=None):
    if not redirect_url:
        redirect_url = 'dashboard'

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


@anonymous_required
def login(request):
    if request.method == 'POST':
        email = request.POST['email'].replace(' ', '').lower()
        password = request.POST['password']

        user = auth.authenticate(username=email, password=password)

        if user:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Credentials or User does not Exist")
            return redirect('login')

    return render(request, 'authorization/login.html', {})


@anonymous_required
def register(request):
    if request.method == 'POST':
        email = request.POST['email'].replace(' ', '').lower()
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if not password1 == password2:
            messages.error(request, "Password do not match!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(
                (request, "A user with the email address: {} already exists, please use a different email.".format(
                    email)))
            return redirect('register')

        user = User.objects.create_user(email=email, username=email, password=password2)
        user.save()

        auth.login(request, user)
        return redirect('dashboard')

    return render(request, 'authorization/register.html', {})

@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')

@anonymous_required
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)

            # Generate password reset token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Build password reset link
            current_site = get_current_site(request)
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_link = f'http://{current_site.domain}{reset_url}'

            # Send password reset email
            mail_subject = 'Reset your password'
            message = render_to_string('authorization/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            email = EmailMessage(mail_subject, message, to=[email])
            email.send()

            messages.success(request, 'Password reset instructions sent to your email.')
        except User.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
        return redirect('forgot_password')

    return render(request, 'authorization/forgot_password.html')
