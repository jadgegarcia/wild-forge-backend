from rest_framework import serializers

from api.models import MeetingCriteria

from .CriteriaSerializer import CriteriaSerializer

class MeetingCriteriaSerializer(serializers.ModelSerializer):
    criteria = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MeetingCriteria
        fields = '__all__'
    
    def get_criteria(self, obj):
        return CriteriaSerializer(obj.criteria_id).data
