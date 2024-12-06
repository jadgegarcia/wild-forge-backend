from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from api.models import ActivityGeminiSettings
from api.serializers import ActivityGeminiSettingsSerializer  # Ensure you have this serializer

class ActivityGeminiSettingsController(viewsets.GenericViewSet,
                                         mixins.ListModelMixin, 
                                         mixins.CreateModelMixin,
                                         mixins.RetrieveModelMixin,
                                         mixins.UpdateModelMixin,
                                         mixins.DestroyModelMixin):
    
    queryset = ActivityGeminiSettings.objects.all()
    serializer_class = ActivityGeminiSettingsSerializer
    authentication_classes = [JWTAuthentication]
    
    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="Get a list of activity criteria settings",
        operation_description="GET /activity-criteria-settings",
        responses={
            status.HTTP_200_OK: ActivityGeminiSettingsSerializer(many=True),
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def list(self, request):
        queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get a specific activity criteria setting by ID",
        operation_description="GET /activity-criteria-settings/{pk}",
        responses={
            status.HTTP_200_OK: ActivityGeminiSettingsSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    def retrieve(self, request, pk=None):
        try:
            settings = ActivityGeminiSettings.objects.get(pk=1)
            serializer = self.get_serializer(settings)
            print(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ActivityGeminiSettings.DoesNotExist:
            return Response({"error": "Activity criteria settings not found"}, status=status.HTTP_404_NOT_FOUND)
