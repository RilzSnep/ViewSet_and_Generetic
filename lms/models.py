from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='previews/courses/', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subscribers = models.ManyToManyField('users.User', related_name='subscribed_courses', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Используем User

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='owned_lessons', null=True)

    def __str__(self):
        return self.title

class Subscription(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'course']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user.email} subscribed to {self.course.title}"

class Payment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey('lms.Course', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    payment_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Payment for {self.course.title} by {self.user.email}"
