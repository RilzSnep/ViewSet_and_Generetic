from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonViewSet, SubscriptionToggleAPIView
from .views import subscription_toggle

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Убрали "api/" для избежания дублирования
    path('subscription/', SubscriptionToggleAPIView.as_view(), name='subscription_toggle'),
    path('subscription/<int:pk>/toggle/', subscription_toggle, name='subscription-toggle'),
]
