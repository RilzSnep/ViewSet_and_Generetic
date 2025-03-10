from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Moderators').exists()


class IsOwnerOrModerator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if IsModerator().has_permission(request, view):
            return True
        return obj.owner == request.user
