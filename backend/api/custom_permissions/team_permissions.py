from rest_framework.permissions import BasePermission

from api.models import TeamMember
from api.models import ClassMember

class IsTeamLeaderOrTeacher(BasePermission):
    def has_permission(self, request, view):
        try:
            user = request.user
            classmember = ClassMember.objects.get(class_id=view.kwargs['class_pk'], user_id=user)
            teammember = TeamMember.objects.get(class_member_id=classmember)
            return teammember.role == TeamMember.LEADER or classmember.role == ClassMember.TEACHER
        except TeamMember.DoesNotExist:
            return classmember.role == ClassMember.TEACHER
        except:
            return False

class IsTeamLeader(BasePermission):
    def has_permission(self, request, view):
        try:
            user = request.user
            classmember = ClassMember.objects.get(class_id=view.kwargs['class_pk'], user_id=user)
            teammember = TeamMember.objects.get(class_member_id=classmember)
            return teammember.role == TeamMember.LEADER
        except:
            return False

class IsTeamMember(BasePermission):
    def has_permission(self, request, view):
        try:
            user = request.user
            classmember = ClassMember.objects.get(class_id=view.kwargs['class_pk'], user_id=user)
            teammember = TeamMember.objects.get(class_member_id=classmember)
            return teammember.role == TeamMember.MEMBER
        except:
            return False
