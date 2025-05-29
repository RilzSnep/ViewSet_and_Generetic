from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonViewSet, SubscriptionToggleAPIView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/subscription/', SubscriptionToggleAPIView.as_view(), name='subscription_toggle'),
]