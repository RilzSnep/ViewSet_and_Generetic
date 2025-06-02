from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', None)  # Устанавливаем username как None
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', None)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True, verbose_name='Имя пользователя')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name='Последняя активность')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments', verbose_name='Пользователь')
    paid_course = models.ForeignKey('lms.Course', on_delete=models.CASCADE, related_name='user_payments', verbose_name='Оплаченный курс')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата платежа')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    payment_method = models.CharField(max_length=50, choices=[('card', 'Карта'), ('transfer', 'Перевод')], verbose_name='Метод оплаты')

    def __str__(self):
        return f"{self.user.email} - {self.paid_course.title} - {self.amount}"

    class Meta:
        verbose_name = 'Платеж пользователя'
        verbose_name_plural = 'Платежи пользователей'
