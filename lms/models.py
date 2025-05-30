from django.db import models
from django.core.validators import MinValueValidator

class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Цена')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='owned_courses', verbose_name='Владелец')
    subscribers = models.ManyToManyField('users.User', related_name='subscribed_courses', verbose_name='Подписчики', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание')
    video_url = models.URLField(verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='owned_lessons', verbose_name='Владелец', null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

class Subscription(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'course')

class Payment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='lms_payments', verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lms_payments', verbose_name='Курс')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    stripe_session_id = models.CharField(max_length=255, verbose_name='ID сессии Stripe', unique=True)
    payment_url = models.URLField(verbose_name='Ссылка на оплату')
    status = models.CharField(max_length=50, verbose_name='Статус', default='pending')

    def __str__(self):
        return f"{self.user.email} - {self.course.title} - {self.amount}"

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
