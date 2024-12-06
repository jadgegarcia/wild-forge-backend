from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from api.custom_permissions import IsTeamLeader

from api.models import Pitch, MeetingPresentor, Team

from api.serializers import PitchSerializer, NoneSerializer

class PitchesController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = Pitch.objects.all()
    serializer_class = PitchSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create','destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsTeamLeader()]
        elif self.action in ['retrieve', 'list', 'join']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    
    @action(detail=False, methods=['POST'])
    def create_pitch(self, request):
        
        # Extract the data from the request
        pitch_data = request.data
        meetingPresentorId = pitch_data["presentor_id"]

        team = Team.objects.get(id=pitch_data["team_id"])
        pitch_data["team_id"] = team
        del pitch_data["presentor_id"]
        pitch = Pitch.objects.create(**pitch_data)

        MeetingPresentor.objects.filter(id=meetingPresentorId).update(pitch_id=pitch.id)
        
        return Response(PitchSerializer(pitch).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['put'])
    def update_pitch(self, request):
        pitch_id = request.query_params.get('pitchId')
        pitch_data = request.data


        # Update the pitch with the specified pitchId
        pitch = Pitch.objects.get(id=pitch_id)
        pitch.name = pitch_data["name"]
        pitch.description = pitch_data["description"]
        pitch.save()

        return Response(PitchSerializer(pitch).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="List all meetings under a classroom.",
        operation_description="GET /meetings/?classroom=classroom&status=status",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', PitchSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=False, methods=['get'])
    def my_pitch(self, request):
        team_id_param = self.request.query_params.get('teamid')
        pitch = Pitch.objects.get(team_id=team_id_param)
        return Response(PitchSerializer(pitch).data, status=status.HTTP_200_OK)