from rest_framework import serializers

from api.models import MeetingPresentor, TeamMember, User, ClassMember

from .PitchSerializer import PitchSerializer

from .TeamSerializer import TeamSerializer

from .UserSerializer import UserSerializer


class MeetingPresentorSerializer(serializers.ModelSerializer):
    pitch = serializers.SerializerMethodField(read_only=True)
    team = serializers.SerializerMethodField(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MeetingPresentor
        fields = '__all__'

    def get_pitch(self, obj):
        return PitchSerializer(obj.pitch_id).data

    def get_team(self, obj):
        return TeamSerializer(obj.team_id).data
    
    def get_members(self, obj):
        team_members = TeamMember.objects.filter(team_id=obj.team_id)
        class_member_ids = team_members.values_list('class_member_id', flat=True)
        class_members = ClassMember.objects.filter(id__in=class_member_ids)
        user_ids = class_members.values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids)
        return UserSerializer(users, many=True).data