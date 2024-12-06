from rest_framework import serializers

from api.models import MeetingComment
from api.models import User
from api.models import ClassMember

class MeetingCommentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MeetingComment
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.classmember_id.user_id.get_full_name()
        