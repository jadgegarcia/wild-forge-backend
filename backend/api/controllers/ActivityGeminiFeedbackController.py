from rest_framework import viewsets, mixins, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from api.custom_permissions import IsTeacher
from api.models import ActivityGeminiFeedback
from api.serializers import ActivityGeminiFeedbackSerializer

class ActivityGeminiFeedbackController(viewsets.GenericViewSet,
                                        mixins.ListModelMixin,
                                        mixins.CreateModelMixin,
                                        mixins.RetrieveModelMixin,
                                        mixins.UpdateModelMixin,
                                        mixins.DestroyModelMixin):
    
    queryset = ActivityGeminiFeedback.objects.all()
    serializer_class = ActivityGeminiFeedbackSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsTeacher()]
        elif self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def feedbacks(self, request):
        queryset = self.get_queryset()  # Use the base queryset for consistency
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
