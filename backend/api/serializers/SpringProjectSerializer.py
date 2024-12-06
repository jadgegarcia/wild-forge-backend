from rest_framework import serializers

from api.models import SpringProject


class SpringProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpringProject
        fields = ('id', 'name', 'description', 'team_id', 'score', 'reason', 'is_active', 'date_created')
        labels = {
            'name': 'Name',
            'description': 'Description',
            'team_id': 'Team ID',
            'score': 'Score',
            'reason': 'Reason',
            'is_active': 'Active/Inactive',
            'date_created': 'Date Created',
        }
