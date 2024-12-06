from rest_framework import serializers

from api.models import SpringBoardTemplate


class SpringBoardTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpringBoardTemplate
        fields = ('id', 'title', 'content', 'rules','description', 'date_created')
        labels = {
            'title': 'Title',
            'content': 'Content',
            'rules': 'Rules',
            'description': 'Description',
            'date_created': 'Date Created',
        }
