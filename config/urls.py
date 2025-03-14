from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonViewSet, SubscriptionToggleAPIView, CreatePaymentAPIView, \
    CheckPaymentStatusAPIView
from users.views import UserViewSet, UserRegisterAPIView, UserDetailAPIView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


def success_view(request):
    return HttpResponse("Оплата успешно завершена!")


def cancel_view(request):
    return HttpResponse("Оплата отменена.")


schema_view = get_schema_view(
    openapi.Info(
        title="LMS API",
        default_version='v1',
        description="API для системы управления обучением (LMS)",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('api/users/<int:pk>/', UserDetailAPIView.as_view(), name='user_detail'),
    path('api/subscription/', SubscriptionToggleAPIView.as_view(), name='subscription_toggle'),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/payment/create/', CreatePaymentAPIView.as_view(), name='create_payment'),
    path('success/', success_view, name='success'),
    path('cancel/', cancel_view, name='cancel'),
    path('api/payment/<int:payment_id>/status/', CheckPaymentStatusAPIView.as_view(), name='check_payment_status'),
]
