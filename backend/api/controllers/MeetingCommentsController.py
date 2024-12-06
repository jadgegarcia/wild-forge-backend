from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from api.models import MeetingComment

from api.serializers import MeetingCommentSerializer

class MeetingCommentsController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = MeetingComment.objects.all()
    serializer_class = MeetingCommentSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def list_comments(self, request, *args, **kwargs):
        meeting = request.query_params.get('meeting')

        try:
            queryset = MeetingComment.objects.all()
            
            queryset = queryset.filter(meeting=meeting)

            serializer = MeetingCommentSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MeetingComment.DoesNotExist:
            return Response({'details': 'Meeting comment not found'}, status=status.HTTP_404_NOT_FOUND)
    