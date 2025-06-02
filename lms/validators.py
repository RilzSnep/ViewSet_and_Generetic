
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


def validate_youtube_url(value):
    logger.debug(f"Проверяю ссылку: {value}")  # Логируем значение для отладки

    if not isinstance(value, str):
        raise ValidationError("Ссылка должна быть строкой.")

    if not value.startswith(
            ('http://youtube.com/', 'https://youtube.com/', 'http://www.youtube.com/', 'https://www.youtube.com/')):
        raise ValidationError("Разрешены только ссылки на youtube.com.")

    return value
