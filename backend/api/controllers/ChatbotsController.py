import os
from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from openai import OpenAI

from api.models import Chatbot
from api.models import Message

from api.serializers import NoneSerializer
from api.serializers import ChatbotSerializer
from api.serializers import MessageSerializer

class ChatbotsController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = Chatbot.objects.all()
    serializer_class = ChatbotSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="Send message to your chatbot",
        operation_description="POST /chatbot/{id}/send",
        request_body=NoneSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', MessageSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['post'])
    def send_message(self, request, *args, **kwargs):
        chatbot = self.get_object()

        leniency_setting = request.data.pop('leniency')
        generality_setting = request.data.pop('generality')
        optimism_setting = request.data.pop('optimism')

        message_serializer = MessageSerializer(data=request.data)

        if message_serializer.is_valid():
            message_serializer.save()
            chatbot.messages.add(message_serializer.data['id'])
        
            constant_messages = [
                {'role': 'system', 'content': 'You are an expert panelist. ... specified ranges from 0 to 1.'},
                {'role': 'system', 'content': f'Configure the panelist with a leniency-to-harsh setting of {leniency_setting}.'},
                {'role': 'system', 'content': f'Now, set the generality-to-specificity configuration to {generality_setting}.'},
                {'role': 'system', 'content': f'Finally, adjust the optimism-to-pessimism setting to {optimism_setting}.'},
                {'role': 'system', 'content': 'Give comments and suggestions on the sent pitch.'},
            ]

            messages = MessageSerializer(instance=chatbot.messages.all(), many=True).data

            destruct_messages = [{'role': message['role'], 'content': message['content']} for message in messages]

            messages_to_be_sent = constant_messages + destruct_messages

            client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))
            openai_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages_to_be_sent,
                temperature=0
            )

            openai_message = {
                'role': openai_response.choices[0].message.role,
                'content': openai_response.choices[0].message.content
            }

            openai_message_serializer = MessageSerializer(data=openai_message)

            if openai_message_serializer.is_valid():
                openai_message_serializer.save()
                chatbot.messages.add(openai_message_serializer.data['id'])
                return Response(openai_message_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(openai_message_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
