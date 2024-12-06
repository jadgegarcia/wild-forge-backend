from rest_framework import serializers

from api.models import Pitch

from .TeamSerializer import TeamSerializer

class PitchSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pitch
        fields = '__all__'

    def get_team(self, obj):
        return TeamSerializer(obj.team_id).data
