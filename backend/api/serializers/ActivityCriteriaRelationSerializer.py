from rest_framework import serializers

from api.models import ActivityCriteriaRelation
from api.serializers.ActivityCriteriaSerializer import ActivityCriteriaSerializer

class ActivityCriteriaRelationSerializer(serializers.ModelSerializer):
    activity_criteria_name = ActivityCriteriaSerializer(source='activity_criteria', read_only=True)

    class Meta:
        model = ActivityCriteriaRelation
        fields = '__all__'