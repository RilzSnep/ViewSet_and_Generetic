import logging
from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def debug_task():
    print("Тестовая задача выполнена!")
    return "Debug task completed"



@shared_task
def send_course_update_email(course_title, subscriber_email):
    logger.info(f"Starting to send email for course '{course_title}' to {subscriber_email}")
    try:
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
        raise


@shared_task
def update_user_activity_status():
    logger.info("Starting task to update user activity status")

    inactivity_threshold = timezone.now() - timedelta(days=30)

    users = User.objects.all()

    for user in users:

        if user.last_login is None or user.last_login < inactivity_threshold:

            if user.is_active:
                user.is_active = False
                user.save()
                logger.info(f"Deactivated user {user.username} due to inactivity")
        else:

            if not user.is_active:
                user.is_active = True
                user.save()
                logger.info(f"Activated user {user.username}")

    logger.info("Finished updating user activity status")
    return "User activity status updated"
