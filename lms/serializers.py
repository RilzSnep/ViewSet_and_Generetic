from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course']  # Можно настроить под ваши нужды


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()  # Оставляем поле количества уроков
    lessons = LessonSerializer(many=True, read_only=True)  # Добавляем поле со списком уроков

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lesson_count', 'lessons']

    def get_lesson_count(self, obj):
        # Метод для вычисления количества уроков
        return obj.lessons.count()
