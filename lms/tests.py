from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from lms.models import Lesson, Course, Subscription

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
            owner=self.user
        )
        self.subscription_url = reverse('subscription-toggle', kwargs={'pk': self.course.id})

    def test_lesson_crud(self):
        # Тест создания урока (Create)
        lesson_data = {
            "title": "New Lesson",
            "description": "New Description",
            "video_url": "https://www.youtube.com/watch?v=new",
            "course": self.course.id,
            "owner": self.user.id
        }
        response = self.client.post('/api/lessons/', lesson_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

        # Тест чтения урока (Read)
        lesson_id = response.data['id']
        response = self.client.get(f'/api/lessons/{lesson_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "New Lesson")

        # Тест обновления урока (Update)
        update_data = {"title": "Updated Lesson"}
        response = self.client.patch(f'/api/lessons/{lesson_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Lesson.objects.get(id=lesson_id).title, "Updated Lesson")

        # Тест удаления урока (Delete)
        response = self.client.delete(f'/api/lessons/{lesson_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_access_control(self):
        # Создаём другого пользователя
        other_user = User.objects.create_user(email="other@example.com", password="otherpass123")
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)

        # Проверяем, что другой пользователь не может редактировать урок
        lesson_id = self.lesson.id
        update_data = {"title": "Hacked Lesson"}
        response = other_client.patch(f'/api/lessons/{lesson_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Проверяем, что другой пользователь не может удалить урок
        response = other_client.delete(f'/api/lessons/{lesson_id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Проверяем, что другой пользователь может читать урок
        response = other_client.get(f'/api/lessons/{lesson_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscription_toggle(self):
        # Тест переключения подписки
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # Тест отписки
        response = self.client.post(self.subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())
