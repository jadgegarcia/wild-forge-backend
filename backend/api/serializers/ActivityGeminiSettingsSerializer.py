from rest_framework import serializers
from api.models import ActivityGeminiSettings

class ActivityGeminiSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityGeminiSettings
        fields = '__all__'
