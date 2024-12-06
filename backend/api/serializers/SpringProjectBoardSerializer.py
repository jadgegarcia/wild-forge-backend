from rest_framework import serializers

from api.models import SpringProjectBoard

class SpringProjectBoardSerializer(serializers.ModelSerializer):
    template_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = SpringProjectBoard
        fields = ('id', 'board_id', 'title', 'template_id', 'feedback', 'recommendation', 'references', 
                  'project_id', 'criteria_feedback', 'date_created', 'score', 'activity_id')
        labels = {
            'board_id': 'Board ID',
            'template_id': 'Template ID',
            'feedback': 'Feedback',
            'recommendation': 'Recommendation',
            'references': 'References',
            'project_id': 'Project ID',
            'criteria_feedback': 'Criteria Feedback',
            'date_created': 'Date Created',
            'score': 'Score',
            'activity_id': 'Activity ID'
        }

