from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from lms.models import Course, Lesson
from rest_framework_simplejwt.tokens import RefreshToken

class LessonAndSubscriptionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password123')
        self.course = Course.objects.create(title='Test Course', description='Test Desc', price=0.00, owner=self.user1)
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Desc',
            video_url='http://example.com/video',
            course=self.course
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_lesson_crud(self):
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, 200)

    def test_access_control(self):
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, 403)

    def test_subscription_toggle(self):
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(f'/api/subscribe/{self.course.id}/')
        self.assertEqual(response.status_code, 201)
        # Проверяем отписку
        response = self.client.post(f'/api/subscribe/{self.course.id}/')
        self.assertEqual(response.status_code, 200)
