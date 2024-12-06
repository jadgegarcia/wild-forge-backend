from uuid import uuid4
from rest_framework import serializers
from rest_framework_nested.relations import NestedHyperlinkedRelatedField

from api.models import ClassRoom

class ClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = ['id', 'course_name', 'sections', 'schedule', 'class_code', 'max_teams_members', 'class_member']
        labels = {
            'course_name': 'Course Name',
            'sections': 'Number of Sections',
            'schedule': 'Schedule',
            'class_code': 'Class Code',
            'max_teams_members': 'Maximum Number of Teams Members'
        }

        # make class_code read-only and update-only
        extra_kwargs = {
            'class_code': {'read_only': True, 'required': False},
            'max_teams_members': {'default': 5}
        }
    
    class_member = NestedHyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='class-class-members-list',
        parent_lookup_kwargs={'class_pk': 'class_id'}
    )

    def create(self, validated_data):
        class_room = ClassRoom.objects.create(**validated_data)
        class_room.class_code = uuid4().hex[:8].upper()
        class_room.save()
        return class_room

            
class JoinClassRoomSerializer(serializers.Serializer):
    class_code = serializers.CharField(max_length=8)

    class Meta:
        ref_name = 'JoinClassInput'