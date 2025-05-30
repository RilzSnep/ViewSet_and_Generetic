from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from users.models import User
from lms.models import Course, Lesson
from rest_framework_simplejwt.tokens import RefreshToken

class LessonAndSubscriptionTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Создаём тестовых пользователей
        self.user1 = User.objects.create_user(email='user1@example.com', password='pass123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='pass123')

        # Очищаем группы
        self.user1.groups.clear()
        self.user2.groups.clear()

        # Создаём курс и урок
        self.course = Course.objects.create(title='Test Course', description='Test Desc', price=0.00, owner=self.user1)
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Desc',
            video_url='http://example.com/video',
            course=self.course
        )

        # Аутентифицируем user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post('/api/token/', {'email': 'user1@example.com', 'password': 'pass123'})
        self.token = response.data['access']

    def test_lesson_crud(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Тест создания урока
        data = {
            'title': 'New Lesson',
            'description': 'New Desc',
            'video_url': 'https://www.youtube.com/watch?v=xyz',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Тест чтения урока
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Тест обновления урока
        update_data = {
            'title': 'Updated Lesson',
            'description': 'Updated Desc',
            'video_url': 'https://www.youtube.com/watch?v=xyz',
            'course': self.course.id
        }
        response = self.client.put(f'/api/lessons/{self.lesson.id}/', data=json.dumps(update_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Тест удаления урока
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_subscription_toggle(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Тест добавления подписки
        response = self.client.post('/api/subscription/', data=json.dumps({'course_id': self.course.id}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')

        # Тест удаления подписки
        response = self.client.post('/api/subscription/', data=json.dumps({'course_id': self.course.id}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')

        # Дополнительная проверка подписки/отписки через другой endpoint
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(f'/api/subscribe/{self.course.id}/')
        self.assertEqual(response.status_code, 201)
        # Проверяем отписку
        response = self.client.post(f'/api/subscribe/{self.course.id}/')
        self.assertEqual(response.status_code, 200)

    def test_access_control(self):
        # Аутентифицируем второго пользователя
        response = self.client.post('/api/token/', {'email': 'user2@example.com', 'password': 'pass123'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        # Проверяем доступ к уроку
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
