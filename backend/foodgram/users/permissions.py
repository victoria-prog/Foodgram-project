from rest_framework import permissions


class IsOwnerOrAuthenticated(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        print(obj)
        if request.user.is_authenticated:
            return (
                request.method in permissions.SAFE_METHODS
                or obj == request.user
            )
        return False
