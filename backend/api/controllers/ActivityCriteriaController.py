from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from api.custom_permissions import IsTeacher

from api.models import ActivityCriteria

from api.serializers.ActivityCriteriaSerializer import ActivityCriteriaSerializer

class ActivityCriteriaController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = ActivityCriteria.objects.all()
    serializer_class = ActivityCriteriaSerializer
    authentication_classes = [JWTAuthentication]
    
    # print("RESULT:\n")
    # print(queryset)

    def get_permissions(self):
        if self.action in ['create','destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['retrieve', 'list', 'join']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def activityCriterias(self, request):
        queryset = ActivityCriteria.objects.all()
        serializer = CriteriaSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Get a specific activity criteria by ID",
        operation_description="GET /activity-criterias/{pk}",
        responses={
            status.HTTP_200_OK: ActivityCriteriaSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        }
    )
    
    def retrieve(self, request, pk=None):
        try:
            activityCriteria = ActivityCriteria.objects.get(pk=pk)
            serializer = self.get_serializer(activityCriteria)
            #print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ActivityCriteria.DoesNotExist:
            return Response({"error": "Activity criteria not found"}, status=status.HTTP_404_NOT_FOUND)