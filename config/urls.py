from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonViewSet  # Импортируем ViewSet из lms
from users.views import UserViewSet, UserRegisterAPIView, UserDetailAPIView

# Настраиваем роутер
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)  # Добавляем маршруты для курсов
router.register(r'lessons', LessonViewSet)  # Добавляем маршруты для уроков

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('api/users/<int:pk>/', UserDetailAPIView.as_view(), name='user_detail'),
    path('api/', include(router.urls)),
]
