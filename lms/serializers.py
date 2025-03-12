# lms/serializers.py
from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url

class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.CharField(max_length=200, validators=[validate_youtube_url], allow_blank=True, required=False)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course']

    def validate(self, data):
        # Проверяем только при создании или обновлении
        if self.context.get('view').action in ['create', 'update', 'partial_update']:
            if 'video_url' in data and data['video_url']:
                validate_youtube_url(data['video_url'])
        return data

class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lesson_count', 'lessons', 'is_subscribed']

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscription.objects.filter(user=user, course=obj).exists()