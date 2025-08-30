from oaback import celery_app
from django.core.mail import send_mail
from django.conf import settings


@celery_app.task(name='send_mail_task')
def send_mail_task(email, message):
    send_mail("【XX企业】账号激活", message=message,
              recipient_list=[email], from_email=settings.DEFAULT_FROM_EMAIL)
