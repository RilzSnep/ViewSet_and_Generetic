from rest_framework.test import APITestCase, APIClient
from users.models import User
from lms.models import Course, Lesson
from rest_framework_simplejwt.tokens import RefreshToken

class TestViews(APITestCase):
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

    def test_some_view(self):
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, 200)
