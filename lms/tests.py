from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from .models import Course, Lesson, Subscription
import json

class LessonAndSubscriptionTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Создаю тестовых пользователей
        self.user1 = User.objects.create_user(email='user1@example.com', password='pass123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='pass123')

        # Очищаю группы
        self.user1.groups.clear()
        self.user2.groups.clear()

        # Создаю курс и урок
        self.course = Course.objects.create(title='Test Course', description='Test Desc', owner=self.user1, price=10.00)
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Desc',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            course=self.course,
            owner=self.user1
        )

        # Получаю токен для user1
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

    def test_access_control(self):
        # Аутентифицируем второго пользователя
        response = self.client.post('/api/token/', {'email': 'user2@example.com', 'password': 'pass123'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

        # Попытка обновления урока другого пользователя
        update_data = {'title': 'Unauthorized Update'}
        response = self.client.put(f'/api/lessons/{self.lesson.id}/', data=json.dumps(update_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)