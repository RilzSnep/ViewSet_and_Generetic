from django.urls import path
from .views import UserViewSet, UserRegisterAPIView, UserDetailAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name="user_detail")
] + router.urls
