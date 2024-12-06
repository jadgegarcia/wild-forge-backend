from rest_framework import serializers

from api.models import Chatbot

from .MessageSerializer import MessageSerializer

class ChatbotSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Chatbot
        fields = '__all__'

    def get_messages(self, obj):
        return MessageSerializer(obj.messages, many=True).data
    