from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from api.custom_permissions import IsTeacher

from api.models import Criteria

from api.serializers import CriteriaSerializer

class CriteriasController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = Criteria.objects.all()
    serializer_class = CriteriaSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create','destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsTeacher()]
        elif self.action in ['retrieve', 'list', 'join']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def criterias(self, request):
        queryset = Criteria.objects.all()
        serializer = CriteriaSerializer(queryset, many=True)
        return Response(serializer.data)
    
