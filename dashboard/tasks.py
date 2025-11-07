from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
import os


@shared_task
def send_bulk_emails(email_list, subject, message, saved_file_path):
    print(saved_file_path)
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=email_list,
    )

    if saved_file_path:
        file_path = os.path.join(settings.MEDIA_ROOT, saved_file_path)
        attachment_name = os.path.basename(file_path)
        print(file_path)
        try:
            with open(file_path, 'rb') as file:
                email.attach(attachment_name, file.read(), 'application/octet-stream')
        except Exception as e:
            print("Error attaching file:", str(e))
    else:
        print("No attachment provided")

    try:
        email.send()
        print("Email sent with attachment")
    except Exception as e:
        print("Error sending email:", str(e))
