from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response

from api.custom_permissions import IsModerator

from api.models import PeerEval
from api.models import ClassRoom
from api.models import ClassMember
from api.models import ClassRoomPE
from api.models import ClassRoomPETaker
from api.serializers import PeerEvalSerializer
from api.serializers import AssignPeerEvalSerializer
from api.serializers import ClassRoomPESerializer
from api.serializers import ClassRoomPETakerSerializer
from api.serializers import NoneSerializer

class PeerEvalsController (viewsets.GenericViewSet,
                        mixins.ListModelMixin, 
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin):
    queryset = PeerEval.objects.all()
    serializer_class = PeerEvalSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        If the action is 'destroy', only allow admin users to access.
        If the action is 'list', only allow authenticated users to access.
        otherwise, return 403 Forbidden.
        """
        if self.action in ['create', 'destroy', 'assign']:
            return [permissions.IsAuthenticated(), IsModerator()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="Lists all peer evals",
        operation_description="GET /evals",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', PeerEvalSerializer(many=True)),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def list(self, request, *args, **kwargs):
        # join ClassroomPE and ClassroomPETaker
        # get all peer evals

        peer_evals = PeerEval.objects.all()
        serializer = PeerEvalSerializer(peer_evals, many=True).data

        for i in range(len(serializer)):
            serializer[i]['assigned_classes'] = []
            class_room_pes = ClassRoomPE.objects.filter(peer_eval_id=serializer[i]['id'])
            for class_room_pe in class_room_pes:
                class_room = ClassRoom.objects.get(id=class_room_pe.class_id.id)
                serializer[i]['assigned_classes'].append({
                    'id': class_room.id,
                    'name': class_room.course_name,
                })

        return Response(serializer, status=status.HTTP_200_OK)

    
        # return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Creates a peer eval",
        operation_description="POST /evals",
        request_body=PeerEvalSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', PeerEvalSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_summary="Retrieves a peer eval",
        operation_description="GET /evals/{id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', PeerEvalSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Updates a peer eval",
        operation_description="PUT /evals/{id}",
        request_body=PeerEvalSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', PeerEvalSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Deletes a peer eval",
        operation_description="DELETE /evals/{id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', PeerEvalSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Assigns a peer eval to  classses",
        operation_description="POST /evals/{id}/assign",
        request_body=AssignPeerEvalSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', PeerEvalSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['post'])
    def assign(self, request, *args, **kwargs):
        try:
            eval = PeerEval.objects.get(id=kwargs['pk'])
            class_id = request.data['class_id']
            classroom = ClassRoom.objects.get(id=class_id)
            classroom_pe = ClassRoomPE.objects.create(
                peer_eval_id=eval,
                class_id=classroom
            )
            classroom_pe.save()
            
            return Response({'detail': 'Assigned peer eval to a class'}, status=status.HTTP_200_OK)
        except PeerEval.DoesNotExist:
            return Response({'detail': 'Peer eval does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # get peer eval by assigned classes
    @swagger_auto_schema(
        operation_summary="Gets all peer evals assigned to a class",
        operation_description="GET /evals/assigned/{class_id}/classmember/{cm_id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=False, methods=['GET'], url_path='assigned/(?P<class_id>[^/.]+)/classmember/(?P<cm_id>[^/.]+)')
    def assigned(self, request, class_id, cm_id, *args, **kwargs):
        try:
            classroom = ClassRoom.objects.get(id=class_id)
            classroom_pes = ClassRoomPE.objects.filter(class_id=classroom)
            classroom_pes_serializer = ClassRoomPESerializer(classroom_pes, many=True).data

            class_member = ClassMember.objects.get(id=cm_id)

            classroom_pe_takers = ClassRoomPETaker.objects.filter(class_member_id=class_member)
            classroom_pe_takers_serializer = ClassRoomPETakerSerializer(classroom_pe_takers, many=True).data

            peerEvals = []
            for classroom_pe in classroom_pes_serializer:
                peerEval = PeerEval.objects.get(id=classroom_pe['peer_eval_id'])
                peerEvalSerializer = PeerEvalSerializer(peerEval).data

                if any(pe_taker['class_room_pe_id'] == classroom_pe['id'] for pe_taker in classroom_pe_takers_serializer):
                    peerEvalSerializer['status'] = ClassRoomPETaker.COMPLETED
                else:
                    peerEvalSerializer['status'] = ClassRoomPETaker.PENDING

                peerEvalSerializer['class_pe_id'] = classroom_pe['id']
                peerEvals.append(peerEvalSerializer)
             
            return Response(peerEvals, status=status.HTTP_200_OK)
        except ClassRoom.DoesNotExist:
            return Response({'detail': 'Class does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'detail': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        operation_summary="Submits a peer eval",
        operation_description="POST /evals/assigned/{class_pe_id}/classmember/{cm_id}/submit",
        request_body=NoneSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=False, methods=['POST'], url_path='assigned/(?P<class_pe_id>[^/.]+)/classmember/(?P<cm_id>[^/.]+)/submit')
    def submit(self, request, class_pe_id, cm_id, *args, **kwargs):
        try:
            classroom_pe = ClassRoomPE.objects.get(id=class_pe_id)
            class_member = ClassMember.objects.get(id=cm_id)

            classroom_pe_taker = ClassRoomPETaker.objects.create(
                class_member_id=class_member,
                class_room_pe_id=classroom_pe,
                status=ClassRoomPETaker.COMPLETED
            )

            classroom_pe_taker.save()

            return Response({'detail': 'Submitted peer eval'}, status=status.HTTP_200_OK)
        except ClassRoom.DoesNotExist:
            return Response({'detail': 'Class does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'detail': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
