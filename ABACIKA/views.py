from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from django.core.validators import validate_email
from django.core.exceptions import ValidationError


# Create your views here.

def home(request):
    return render(request, 'landing/home.html', {})

def contact(request):
    if request.method == 'POST':
        # Get the form data
        first_name = request.POST.get('fname', '')
        last_name = request.POST.get('lname', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        # Compose the email message
        email_message = f"Name: {first_name} {last_name}\n\nEmail: {email}\n\nMessage: {message}"

        # Send the email
        send_mail(
            subject,
            email_message,
            email,
            ['teamabacika@gmail.com'],  # Replace with the recipient's email address
            fail_silently=False,
        )

        # Set success message
        messages.success(request, 'Your email has been sent successfully!')
        return redirect('contact')

    return render(request, 'landing/contact.html')


def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('newsletter')

        # The email subscription logic here
        # For example, we can save the email to a database or send it to an external service
        # and we'll send a confirmation email to the subscriber

        # Send confirmation email
        subject = 'Newsletter Subscription Confirmation'
        message = 'Thank you for subscribing to our newsletter!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]

        try:
            send_mail(subject, message, from_email, to_email)
            # Display a success message to the user
            messages.success(request, 'You have successfully subscribed to the newsletter.')
            return redirect('newsletter')

        except Exception as e:
            pass

    return render(request, 'landing/newsletter.html')
