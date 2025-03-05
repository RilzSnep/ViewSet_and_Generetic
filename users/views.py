from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]  # Включаем фильтрацию
    filterset_fields = {
        'payment_date': ['exact', 'lt', 'gt'],  # Фильтрация и сортировка по дате
        'paid_course': ['exact'],  # Фильтрация по курсу
        'paid_lesson': ['exact'],  # Фильтрация по уроку
        'payment_method': ['exact'],  # Фильтрация по способу оплаты
    }
    ordering_fields = ['payment_date']  # Поле для сортировки
    ordering = ['payment_date']  # Сортировка по умолчанию (по дате оплаты)
