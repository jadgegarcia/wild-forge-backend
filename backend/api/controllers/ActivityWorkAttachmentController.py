from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.custom_permissions import IsTeacher, IsStudent, IsBasic

from api.models import Activity
from api.models import ActivityTemplate
from api.models import ClassRoom
from api.models import Team
from api.models import ActivityWorkAttachment

from api.serializers import ActivityWorkAttachmentSerializer
from api.serializers import ActivitySerializer
from api.serializers import ActivityTemplateSerializer
from api.serializers import ActivityCreateFromTemplateSerializer
from api.serializers import ClassRoomSerializer
from api.serializers import TeamSerializer

import fitz

class ActivityWorkAttachmentController(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = ActivityWorkAttachment.objects.all()
    serializer_class = ActivityWorkAttachmentSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create', 'update', 
                           'destroy',
                           ]:
            return [permissions.IsAuthenticated(), IsBasic()]
        else:
            return [permissions.IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="Add work attachment to an activity",
        operation_description="POST /activity-work-attachments",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', ActivityWorkAttachmentSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Invalid or missing data in the request.'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. Associated Activity not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            activity_id = request.data.get('activity_id', None)

            if activity_id:
                try:
                    activity = Activity.objects.get(pk=activity_id)
                    serializer.save(activity_id=activity_id)  # Set activity_id directly
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Activity.DoesNotExist:
                    return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Activity ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_summary="Update work attachment",
        operation_description="PUT /activity-work-attachments/{id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivityWorkAttachmentSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Invalid or missing data in the request.'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. Work attachment not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_summary="Delete work attachment",
        operation_description="DELETE /activity-work-attachments/{id}",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('No Content', message='Work attachment deleted successfully.'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. Work attachment not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_summary="Get all work attachments for a specific activity",
        operation_description="GET /activity-work-attachments/activity/{activity_id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivityWorkAttachmentSerializer(many=True)),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. Activity not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    @action(detail=False, methods=['GET'], url_path='activities/(?P<activity_id>[^/.]+)')
    def activity_work_attachments(self, request, *args, **kwargs):
        activity_id = kwargs.get('activity_id', None)
        if activity_id is not None:
            try:
                activity = Activity.objects.get(pk=activity_id)
                attachments = ActivityWorkAttachment.objects.filter(activity_id=activity)
                serializer = ActivityWorkAttachmentSerializer(attachments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Activity.DoesNotExist:
                return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Activity ID not provided'}, status=status.HTTP_400_BAD_REQUEST)