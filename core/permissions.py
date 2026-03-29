from rest_framework import permissions
from .models import User

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsDirectorOrSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.role == User.Role.DIRECTEUR)

class IsDepotChiefOrHigher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated