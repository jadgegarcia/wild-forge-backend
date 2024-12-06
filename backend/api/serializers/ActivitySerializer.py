from rest_framework import serializers
from api.models import Activity
from api.serializers import SpringProjectSerializer

class ActivitySerializer(serializers.ModelSerializer):
    spring_project = SpringProjectSerializer(required=False)  # Make it not required

    class Meta:
        model = Activity
        fields = ('id', 'classroom_id', 'team_id', 'activityCriteria_id', 'title', 'description', 'instruction', 'submission_status', 'date_created', 'due_date', 'evaluation', 'total_score','return_status', 'spring_project')

class ActivityCreateFromTemplateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    team_ids = serializers.ListField(child=serializers.IntegerField())
    # activityCriteria_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    due_date = serializers.DateTimeField()
    evaluation = serializers.IntegerField()
    total_score = serializers.IntegerField()
    class_id = serializers.IntegerField() 