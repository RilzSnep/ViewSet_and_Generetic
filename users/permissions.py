from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Moderators').exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'course'):
            return obj.course.owner == request.user
        return obj.owner == request.user
class IsOwnerOrModerator(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ модераторам
        if request.user.groups.filter(name='Moderators').exists():
            return True
        # Если объект — Lesson, проверяем владельца курса
        if hasattr(obj, 'course'):
            return obj.course.owner == request.user
        # Для других объектов (например, Course) проверяем owner
        return obj.owner == request.user
