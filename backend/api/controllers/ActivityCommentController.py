import json


from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.custom_permissions import IsTeacher, IsModerator

from api.models import ActivityComment
from api.models import User
from api.models import Activity

from api.serializers import ActivityCommentSerializer, ActivityCommentWithUserSerializer, UserCommentSerializer, SpecificActivityCommentSerializer, CommentCreateSerializer

class ActivityCommentController(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = ActivityComment.objects.all()
    authentication_classes = [JWTAuthentication]


    def extract_feedback(self, feedback_string):
        start_index = feedback_string.find("'feedback':") + len("'feedback':")
        end_index = feedback_string.find("}]", start_index)
        if start_index != -1 and end_index != -1:
            return feedback_string[start_index:end_index].strip()
        else:
            return "Feedback not found in the input string."


    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 
                           'destroy'
                           ]:
            return [permissions.IsAuthenticated(), IsModerator()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        else:
            return ActivityCommentSerializer

    @swagger_auto_schema(
        operation_summary="Create an activity comment",
        operation_description="POST /activity-comments",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', ActivityCommentSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Invalid or missing data in the request.'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. Associated Activity or User not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_id = request.data.get('user_id', None)
            activity_id = request.data.get('activity_id', None)

            if user_id and activity_id:
                try:
                    user = User.objects.get(pk=user_id)
                    activity = Activity.objects.get(pk=activity_id)
                    serializer.save(user_id=user_id, activity_id=activity_id)  # Set user and activity directly
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                except Activity.DoesNotExist:
                    return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'User ID or Activity ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_summary="Get all comments for a specific activity",
        operation_description="GET /activity-comments/get-activity-comments/{activity_id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivityCommentSerializer(many=True)),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Activity not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    @action(detail=False, methods=['GET'], url_path='activities/(?P<activity_id>[^/.]+)')
    def get_activity_comments(self, request, *args, **kwargs):
        activity_id = kwargs.get('activity_id', None)
    
        if activity_id is not None:
            try:
                activity = Activity.objects.get(pk=activity_id)
                comments = ActivityComment.objects.filter(activity_id=activity)

                # comments[0].comment = self.extract_feedback(comments[0].comment)

                #print(edited)
                serializer = ActivityCommentWithUserSerializer(comments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Activity.DoesNotExist:
                return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Activity ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Get a specific comment by ID",
        operation_description="GET /activity-comments/{pk}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivityCommentWithUserSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Comment not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ActivityCommentWithUserSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @swagger_auto_schema(
        operation_summary="Delete an activity comment",
        operation_description="DELETE /activity-comments/{pk}",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('No Content'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Comment not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="Update an activity comment",
        operation_description="PUT /activity-comments/{pk}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivityCommentSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Invalid or missing data in the request.'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Comment not found.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="List all activity comments",
        operation_description="GET /activity-comments",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivityCommentSerializer(many=True)),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ActivityCommentWithUserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        
