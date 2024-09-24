
from rest_framework.permissions import BasePermission
from rest_framework import permissions

class AllowAny(permissions.BasePermission):
    """
    Custom permission to allow any user to access the view.
    """
    def has_permission(self, request, view):
        return True  # Always allow access

class IsAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated