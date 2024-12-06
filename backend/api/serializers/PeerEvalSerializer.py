from rest_framework import serializers

from api.models import PeerEval

class PeerEvalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeerEval
        fields = ['id', 'name', 'forms_link', 'sheet_link', 'date_created', 'date_updated']
        labels = {
            'name': 'Name',
            'forms_link': 'Forms Link',
            'sheet_link': 'Sheet Link',
            'date_created': 'Date Created',
            'date_updated': 'Date Updated',
        }

class AssignPeerEvalSerializer(serializers.Serializer):
    class_id = serializers.IntegerField()