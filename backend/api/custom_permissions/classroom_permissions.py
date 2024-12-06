from rest_framework.permissions import BasePermission

from api.models import ClassMember

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        try:
            user = request.user
            class_member = ClassMember.objects.get(class_id=view.kwargs['class_pk'], user_id=user)
            return class_member.role == ClassMember.TEACHER
        except:
            return False
    
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        try:
            user = request.user
            class_member = ClassMember.objects.get(class_id=view.kwargs['class_pk'], user_id=user)
            return class_member.role == ClassMember.STUDENT
        except:
            return False
    
class IsClassMember(BasePermission):
    def has_permission(self, request, view):
        try:
            user = request.user
            class_member = ClassMember.objects.get(class_id=view.kwargs['class_pk'], user_id=user)
            return class_member.status == ClassMember.ACCEPTED
        except:
            return False