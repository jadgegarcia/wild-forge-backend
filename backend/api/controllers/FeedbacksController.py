import os
from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from openai import OpenAI

from api.custom_permissions import IsTeacher

from api.models import Feedback
from api.models import Remark

from api.serializers import FeedbackSerializer
from api.serializers import RemarkSerializer

class FeedbacksController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create','destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsTeacher()]
        elif self.action in ['retrieve', 'list', 'join']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="Creates a new feedback for a pitch in a specific meeting",
        operation_description="POST /feedbacks",
        request_body=FeedbackSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', FeedbackSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def create(self, request, *args, **kwargs):
        meeting = request.data.get('meeting')
        pitch = request.data.get('pitch')
        
        if not meeting:
            return Response({'meeting': 'This is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not pitch:
            return Response({'pitch': 'This is required.'}, status=status.HTTP_400_BAD_REQUEST)

        remarks = RemarkSerializer(instance=Remark.objects.filter(meeting_id=meeting, pitch_id=pitch), many=True).data

        prompt = '\n\n'.join(remark['remark'] for remark in remarks if 'remark' in remark)

        complete_prompt = f'Please provide a concise summary of the remarks. Highlight key strengths and areas for improvement mentioned by each evaluator. Provide it into a single paragraph.{prompt}'

        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        openai_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                'role': 'user', 'content': complete_prompt
            }],
            temperature=0
        )

        feedback = {
            'pitch': pitch,
            'meeting': meeting,
            'feedback': openai_response.choices[0].message.content
        }

        feedback_serializer = FeedbackSerializer(data=feedback)

        if feedback_serializer.is_valid():
            feedback_serializer.save()
            return Response(feedback_serializer.data, status=status.HTTP_201_CREATED)
        return Response(feedback_serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
