from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from api.models import ActivityCriteriaRelation
from api.serializers import ActivityCriteriaRelationSerializer  # Make sure to create this serializer

class ActivityCriteriaRelationController(viewsets.GenericViewSet,
                                         mixins.ListModelMixin,
                                         mixins.CreateModelMixin,
                                         mixins.RetrieveModelMixin,
                                         mixins.UpdateModelMixin,
                                         mixins.DestroyModelMixin):
    
    queryset = ActivityCriteriaRelation.objects.all()
    serializer_class = ActivityCriteriaRelationSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def activityRelations(self, request):
        queryset = ActivityCriteriaRelation.objects.all()
        serializer = ActivityCriteriaRelationSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get a specific activity criteria relation by ID",
        operation_description="GET /activity-criteria-relations/{pk}",
        responses={
            status.HTTP_200_OK: ActivityCriteriaRelationSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    
    def retrieve(self, request, pk=None):
        try:
            activity_relation = ActivityCriteriaRelation.objects.get(pk=pk)
            serializer = self.get_serializer(activity_relation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ActivityCriteriaRelation.DoesNotExist:
            return Response({"error": "Activity criteria relation not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary="Get activity criteria relations by activity_id",
        operation_description="GET /activity-criteria-relations/by-activity-id/{activity_id}",
        responses={
            status.HTTP_200_OK: ActivityCriteriaRelationSerializer(many=True),
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        }
    )
    @action(detail=False, methods=['get'], url_path='by-activity-id/(?P<activity_id>\d+)')
    def by_activity_id(self, request, activity_id=None):
        if not activity_id:
            return Response({"error": "activity_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter ActivityCriteriaRelation by activity_id
        queryset = ActivityCriteriaRelation.objects.filter(activity_id=activity_id)
        
        if not queryset.exists():
            return Response({"error": "No activity criteria relations found for this activity_id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ActivityCriteriaRelationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
