from rest_framework import serializers

from api.models import ClassMember, User, ClassRoom
from .UserSerializer import UserSerializer

class ClassMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassMember
        fields = ['id', 'user_id','class_id', 'role', 'status', 'date_created', 'date_updated']
        labels = {
            'user_id': 'User ID',
            'class_id': 'Class ID',
            'role': 'Role',
            'status': 'Status',
            'date_created': 'Date Created',
            'date_updated': 'Date Updated',
        }

        # disable input data body for PUT and PATCH requests
        extra_kwargs = {
            'user_id': {'read_only': True, 'required': False},
            'class_id': {'read_only': True, 'required': False},
            'role': {'read_only': True, 'required': False},
            'status': {'read_only': True, 'required': False},
            'date_created': {'read_only': True, 'required': False},
            'date_updated': {'read_only': True, 'required': False},
        }