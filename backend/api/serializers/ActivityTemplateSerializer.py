from rest_framework import serializers
from api.models import ActivityTemplate

class ActivityTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityTemplate
        fields = ('id', 'course_name', 'title', 'description', 'instructions')
