from rest_framework import serializers

from api.models import Rating
from api.serializers import PitchSerializer

class RatingSerializer(serializers.ModelSerializer):
    pitch = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Rating
        fields = '__all__'

    def get_pitch(self, obj):
        return PitchSerializer(obj.pitch_id).data