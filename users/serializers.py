from rest_framework import serializers
from .models import Payment, User
from lms.models import Course, Lesson


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar']
        read_only_fields = ['id']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'phone', 'city', 'avatar']

    def create(self, validate_data):
        user = User.objects.create_user(
            email=validate_data['email'],
            password=validate_data['password'],
            phone=validate_data.get('phone', ''),
            city=validate_data.get('city', ''),
            avatar=validate_data.get('avatar', None)
        )
        return user


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    paid_course = serializers.StringRelatedField()
    paid_lesson = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method']
