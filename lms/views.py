from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import IsModerator, IsOwnerOrModerator
from .models import Course, Lesson, Subscription, Payment
from .paginators import CustomPagination
from .serializers import CourseSerializer, LessonSerializer
from .services import create_stripe_price, create_stripe_product, create_stripe_checkout_session, check_stripe_session


class SubscriptionToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')  # Получаем id курса из тела запроса
        course = get_object_or_404(Course, id=course_id)

        # Проверяем, есть ли подписка
        subs_item = Subscription.objects.filter(user=user, course=course)

        if subs_item.exists():
            subs_item.delete()  # Удаляем подписку
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)  # Создаём подписку
            message = 'Подписка добавлена'

        return Response({"message": message})


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['destroy', 'update', 'partial_update', 'retrieve']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]  # Исправляем права
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


import logging

logger = logging.getLogger(__name__)


class CreatePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Запрос получен в CreatePaymentAPIView")
        logger.info(f"Данные запроса: {request.data}")

        user = request.user
        course_id = request.data.get('course_id')
        logger.info(f"Course ID: {course_id}")

        course = get_object_or_404(Course, id=course_id)
        logger.info(f"Курс найден: {course.title}")

        if course.price <= 0:
            return Response({"error": "Цена курса должна быть больше 0"}, status=400)

        product = create_stripe_product(course)
        price = create_stripe_price(course, product.id)
        session = create_stripe_checkout_session(user, course, price.id)

        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=course.price,
            stripe_session_id=session.id,
            payment_url=session.url,
        )

        logger.info(f"Создан платёж: ID={payment.id}, URL={payment.payment_url}")

        return Response({
            'payment_url': payment.payment_url,
            'payment_id': payment.id,
        })


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class CheckPaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id, *args, **kwargs):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        status = check_stripe_session(payment.stripe_session_id)
        payment.status = status
        payment.save()
        return Response({"payment_id": payment.id, "status": payment.status})


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
