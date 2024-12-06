from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from api.models import Rating, ClassMember
from api.serializers import RatingSerializer, NoneSerializer

class RatingsController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_summary="List all rating of a specific account",
        operation_description="GET /ratings/my_ratings/",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', RatingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=False, methods=['get'])
    def my_ratings(self, request, *args, **kwargs):
        pitch_param = request.query_params.get('pitch')
        meeting_param = request.query_params.get('meeting')

        try:
            classmember = ClassMember.objects.get(user_id=request.user)
            queryset = Rating.objects.filter(classmember_id=classmember)
            
            if meeting_param:
                queryset = queryset.filter(meeting_id=meeting_param)
            
            if  pitch_param:
                queryset = queryset.filter(pitch_id=pitch_param)
            
            serializer = RatingSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ClassMember.DoesNotExist:
            return Response({'details': 'Class member not found'}, status=status.HTTP_404_NOT_FOUND)
        