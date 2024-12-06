from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Count

from api.custom_permissions import IsTeacher, IsModerator

from api.models import ActivityTemplate

from api.serializers import ActivityTemplateSerializer

class ActivityTemplateController(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = ActivityTemplate.objects.all()
    serializer_class = ActivityTemplateSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create', 'by_course', 'retrieve', 'update', 
                           'destroy', 'list',
                           ]:
            return [permissions.IsAuthenticated(), IsModerator()]
        else:
            return [permissions.IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="Create a new activity template",
        operation_description="POST /activity-templates",
        request_body=ActivityTemplateSerializer,
        responses={
            status.HTTP_201_CREATED: ActivityTemplateSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_summary="Get templates by course",
        operation_description="GET /activity-templates/by-course",
        manual_parameters=[
            openapi.Parameter('course_name', openapi.IN_QUERY, description="Course name", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            status.HTTP_200_OK: ActivityTemplateSerializer(many=True),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    @action(detail=False, methods=['GET'])
    def by_course(self, request):
        course_name = request.query_params.get('course_name', None)

        if course_name is not None:
            templates = ActivityTemplate.objects.filter(course_name=course_name)
            serializer = self.get_serializer(templates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Course name not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_summary="Retrieve an activity template",
        operation_description="GET /activity-templates/{pk}",
        responses={
            status.HTTP_200_OK: ActivityTemplateSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def retrieve(self, request, pk=None):
        try:
            template = ActivityTemplate.objects.get(pk=pk)
            serializer = self.get_serializer(template)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ActivityTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary="Update an activity template",
        operation_description="PUT /activity-templates/{pk}",
        request_body=ActivityTemplateSerializer,
        responses={
            status.HTTP_200_OK: ActivityTemplateSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def update(self, request, pk=None):
        try:
            template = ActivityTemplate.objects.get(pk=pk)
            serializer = self.get_serializer(template, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ActivityTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary="Delete an activity template",
        operation_description="DELETE /activity-templates/{pk}",
        responses={
            status.HTTP_204_NO_CONTENT: "No Content",
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def destroy(self, request, pk=None):
        try:
            template = ActivityTemplate.objects.get(pk=pk)
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ActivityTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        operation_summary="List all activity templates",
        operation_description="GET /activity-templates",
        responses={
            status.HTTP_200_OK: ActivityTemplateSerializer(many=True),
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def list(self, request, *args, **kwargs):
        templates = ActivityTemplate.objects.all()
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Get all courses",
        operation_description="GET /activity-templates/all-courses",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivityTemplateSerializer(many=True)),
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    @action(detail=False, methods=['GET'])
    def get_all_courses(self, request):
        courses = ActivityTemplate.objects.values('course_name').annotate(total=Count('course_name')).order_by('-total')
        # 'values' method retrieves unique course names and 'annotate' adds the total count
        return Response(courses, status=status.HTTP_200_OK)