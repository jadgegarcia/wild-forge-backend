from rest_framework.permissions import BasePermission

from api.models import User

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.MODERATOR
    
class IsBasic(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.BASIC