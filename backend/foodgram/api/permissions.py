from rest_framework import permissions


class OwnerOrReadonly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.method in permissions.SAFE_METHODS
                or obj.author == request.user
            )
        return request.method in permissions.SAFE_METHODS
