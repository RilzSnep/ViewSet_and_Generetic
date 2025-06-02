from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import IsModerator, IsOwnerOrModerator, IsOwnerOrReadOnly
from .models import Course, Lesson, Subscription, Payment
from .paginators import CustomPagination
from .serializers import CourseSerializer, LessonSerializer
from .services import create_stripe_price, create_stripe_product, create_stripe_checkout_session, check_stripe_session
import logging
from .tasks import debug_task, send_course_update_email

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['POST'])
def subscription_toggle(request, pk):
    user = request.user
    course = Course.objects.get(id=pk)
    subscription, created = Subscription.objects.get_or_create(user=user, course=course)
    if not created:
        subscription.delete()
        return Response({"message": "Subscription removed"}, status=status.HTTP_200_OK)
    return Response({"message": "Subscription created"}, status=status.HTTP_201_CREATED)

class SubscriptionToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course)
        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
        return Response({"message": message})

class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = Course.objects.get(id=course_id)
        user = request.user
        if course.subscribers.filter(id=user.id).exists():
            course.subscribers.remove(user)
            return Response({"detail": "Unsubscribed"}, status=status.HTTP_200_OK)
        course.subscribers.add(user)
        return Response({"detail": "Subscribed"}, status=status.HTTP_201_CREATED)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        course = serializer.save()
        subscriptions = Subscription.objects.filter(course=course)
        for subscription in subscriptions:
            send_course_update_email.delay(
                course_title=course.title,
                subscriber_email=subscription.user.email
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        print(f"Обновление курса {instance.title}, подписчики: {instance.subscribers.all()}")
        for subscriber in instance.subscribers.all():
            print(f"Отправка задачи для {subscriber.email}")
            send_course_update_email.delay(course_title=instance.title, subscriber_email=subscriber.email)
        return Response(serializer.data)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CustomPagination
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['destroy', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action in ['retrieve']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

class CreatePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
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
        debug_task.delay()
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
