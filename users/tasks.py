from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task(bind=True, max_retries=3)
def send_mail(self, subject, email, template_name, context):
    try:
        html_content = render_to_string(
            template_name,
            context
        )

        message = EmailMessage(
            subject=subject,
            body=html_content,
            to=[email],
        )
        message.content_subtype = "html"
        message.send()

    except Exception as e:
        self.retry(exc=e, countdown=10)
