# lms/tasks.py
import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def debug_task():
    print("Тестовая задача выполнена!")
    return "Debug task completed"

logger = logging.getLogger(__name__)

@shared_task
def send_course_update_email(course_title, subscriber_email):
    logger.info(f"Starting to send email for course '{course_title}' to {subscriber_email}")
    try:
        # Здесь ваш код для отправки письма, например, через Django's send_mail
        from django.core.mail import send_mail
        send_mail(
            subject=f"Update: {course_title}",
            message=f"Dear subscriber, the course {course_title} has been updated!",
            from_email="your_email@example.com",
            recipient_list=[subscriber_email],
            fail_silently=False,
        )
        logger.info(f"Email successfully sent to {subscriber_email} for course '{course_title}'")
        return f"Email sent to {subscriber_email}"
    except Exception as e:
        logger.error(f"Failed to send email to {subscriber_email}: {str(e)}")
        raise  # Повторно вызываем исключение, чтобы Celery зарегистрировал ошибку
