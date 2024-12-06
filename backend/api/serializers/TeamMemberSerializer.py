from rest_framework import serializers

from api.models import TeamMember

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'class_member_id', 'team_id', 'role', 'status', 'date_created', 'date_updated']
        labels = {
            'class_member_id': 'Class Member ID',
            'team_id': 'Team ID',
            'role': 'Role',
            'status': 'Status',
            'date_created': 'Date Created',
            'date_updated': 'Date Updated'
        }

        # disable input data body for PUT and PATCH requests
        extra_kwargs = {
            'class_member_id': {'read_only': True, 'required': False},
            'team_id': {'read_only': True, 'required': False},
            'role': {'default': TeamMember.MEMBER, 'required': False},
            'status': {'default': TeamMember.PENDING, 'required': False},
            'date_created': {'read_only': True, 'required': False},
            'date_updated': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
    
