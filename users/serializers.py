from rest_framework import serializers
from .models import Payment
from lms.models import Course, Lesson


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    paid_course = serializers.StringRelatedField()
    paid_lesson = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method']
