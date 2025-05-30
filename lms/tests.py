from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from lms.models import Lesson, Course, Subscription
import json

User = get_user_model()

class LessonAndSubscriptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            price=100.00,
            owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Description",
            video_url="https://www.youtube.com/watch?v=xyz",
            course=self.course,
            owner=self.user  # Используем owner=self.user вместо owner_id=self.user.id
        )
        self.subscription_url = reverse('subscription-toggle', kwargs={'pk': self.course.id})

    def test_lesson_crud(self):
        # Тест CRUD операций для Lesson
        pass

    def test_access_control(self):
        # Тест контроля доступа
        pass

    def test_subscription_toggle(self):
        # Тест переключения подписки
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())
