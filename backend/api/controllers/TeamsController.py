from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.db.models import Count, F

from api.custom_permissions import IsTeamLeader

from api.models import Team
from api.models import TeamMember
from api.models import ClassMember
from api.models import ClassRoom
from api.models import User

from api.serializers import TeamSerializer
from api.serializers import NoneSerializer
from api.serializers import TeamMemberSerializer
class TeamsController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        If the action is 'create', 'destroy', 'update', or 'partial_update', only allow admin users to access.
        If the action is 'retrieve', 'list', or 'join', only allow authenticated users to access.
        otherwise, return 403 Forbidden.
        """
        if self.action in ['create','destroy', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsTeamLeader()]
        elif self.action in ['retrieve', 'list', 'join']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="Creates a new team",
        operation_description="POST /teams",
        request_body=TeamSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', TeamSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            class_id = kwargs['class_pk']
            class_member = ClassMember.objects.filter(user_id=request.user, class_id=class_id).first()

            teammember = TeamMember.objects.get(class_member_id=class_member)
            
            # check if user is already in a team
            if teammember.team_id is not None:
                return Response({"error": "You cannot create morethan 1 team."}, status=status.HTTP_400_BAD_REQUEST)

            response = super().create(request, *args, **kwargs)
            new_team = Team.objects.get(id=response.data['id'])
            teammember.team_id = new_team
            teammember.save()
        except:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response
    
    @swagger_auto_schema(
        operation_summary="Updates a team",
        operation_description="PUT /teams/{id}",
        request_body=TeamSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', TeamSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Deletes a team",
        operation_description="DELETE /teams/{id}",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('No Content'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Gets a team",
        operation_description="GET /classes/{class_pk}/teams",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', TeamSerializer),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def list(self, request, *args, **kwargs):
        try:
            class_id = kwargs['class_pk']

            # get all team members by class_id and group by team_id and each team members should include the user's first_name and last_name
            team_members = (
            TeamMember.objects
                .filter(class_member_id__class_id=class_id)
                # add filter if the TeamMember team_id is not null
                .exclude(team_id=None)
                .select_related('class_member_id__user_id')  # Join with ClassMember and User
                .annotate(
                    first_name=F('class_member_id__user_id__first_name'),  # Access User's first_name through ClassMember
                    last_name=F('class_member_id__user_id__last_name'),    # Access User's last_name through ClassMember
                )
                .values(
                    'id',
                    'class_member_id',
                    'role',
                    'status',
                    'team_id',
                    'first_name',  # Access User's first_name through ClassMember
                    'last_name',   # Access User's last_name through ClassMember
                    'date_created',
                    'date_updated',
                )
            )

            # Group team members by team_id
            grouped_team_members = {}
            for team_member in team_members:
                team_id = team_member['team_id']
                if team_id not in grouped_team_members:
                    grouped_team_members[team_id] = []
                grouped_team_members[team_id].append(team_member)

            # Create final teams list with grouped team members
            teams = []
            for team_id, team_members_list in grouped_team_members.items():
                team = Team.objects.get(id=team_id)
                team_data = {
                    'id': team_id,
                    'name': team.name,
                    'description': team.description,
                    'status': team.status,
                    'team_members': team_members_list
                }
                teams.append(team_data)

            return Response(teams, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_summary="Gets a team",
        operation_description="GET /teams/{id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', TeamSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        team_members = TeamMember.objects.filter(team_id=response.data['id'])
        response.data['team_members'] = TeamMemberSerializer(team_members, many=True).data
        return response

    @swagger_auto_schema(
        operation_summary="Gets a team",
        operation_description="GET /teams/my_team",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', TeamSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=False, methods=['get'])
    def my_team(self, request):
        classMember = ClassMember.objects.get(id=request.user)
        team_member = TeamMember.objects.get(class_member_id=classMember.id)
        team = Team.objects.get(id=team_member)
        return Response(TeamSerializer(team).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Updates a team partially",
        operation_description="PATCH /teams/{id}",
        request_body=TeamSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', TeamSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    
    @swagger_auto_schema(
        method='PUT',
        operation_summary="Post Hiring",
        operation_description="PUT /teams/{id}/open",
        request_body=NoneSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', TeamSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['PUT'])
    def open(self, request, *args, **kwargs):
        try:
            classroom = ClassRoom.objects.get(id=kwargs['class_pk'])
            team = Team.objects.get(id=kwargs['pk'])

            # Check if the recruitment status is OPEN
            if team.status == Team.OPEN:
                return Response({"detail": "Team is already open for hiring"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the current number of team members is less than max_members
            current_members_count = TeamMember.objects.filter(team_id=team, status=TeamMember.ACCEPTED).count()
            if current_members_count >= classroom.max_teams_members:
                return Response({"detail": "The team has reached the maximum number of members."}, status=status.HTTP_400_BAD_REQUEST)

            # If all conditions are met, update status
            team.status = Team.OPEN
            team.save()

            return Response({"detail": "Team is now open for hiring"}, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response({"error": "Team does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        method='PUT',
        operation_summary="Close Hiring",
        operation_description="PUT /teams/{id}/close",
        request_body=NoneSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('No Content'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['PUT'])
    def close(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=kwargs['pk'])

            # Check if the recruitment status is CLOSE
            if team.status == Team.CLOSE:
                return Response({"detail": "Team is already closed for hiring"}, status=status.HTTP_400_BAD_REQUEST)

            # If all conditions are met, update status
            team.status = Team.CLOSE
            team.save()
            return Response({"detail": "Team is now closed for hiring"}, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response({"error": "Team does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    # ENDPOINT FOR A CLASS MEMBER TO APPLY TO A HIRING POST
    @swagger_auto_schema(
        operation_summary="Apply to a team",
        operation_description="POST /teams/{id}/join",
        request_body=NoneSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', TeamSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['post'])
    def join(self, request, *args, **kwargs):
        try:
            classroom = ClassRoom.objects.get(id=kwargs['class_pk'])
            team = Team.objects.get(id=kwargs['pk'])
            
            # Check if the recruitment status is CLOSE
            if team.status == Team.CLOSE:
                return Response({"detail": "Team is closed for hiring"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the current number of team members is less than max_members
            current_members_count = TeamMember.objects.filter(team_id=team, status=TeamMember.ACCEPTED).count()
            if current_members_count >= classroom.max_teams_members:
                return Response({"detail": "The team has reached the maximum number of members."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user is already a member of the team
            class_member = ClassMember.objects.get(user_id=request.user)
            if TeamMember.objects.filter(team_id=team, class_member_id=class_member, status=TeamMember.ACCEPTED).exists():
                return Response({"detail": "You are already a member of this team."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the user has already applied to the team
            if TeamMember.objects.filter(team_id=team, class_member_id=class_member, status=TeamMember.PENDING).exists():
                return Response({"detail": "You have already applied to this team."}, status=status.HTTP_400_BAD_REQUEST)
            
            # If all conditions are met, create a team member with status pending
            team_member = TeamMember.objects.create(
                class_member_id=class_member,
                team_id=team,
                role=TeamMember.MEMBER,
                status=TeamMember.PENDING
            )
            team_member.save()
            serializer = TeamMemberSerializer(team_member)

            return Response(serializer.data)
        except ClassRoom.DoesNotExist:
            return Response({"error": "Class does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response({"error": "Team does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
