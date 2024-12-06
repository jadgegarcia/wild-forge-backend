import os
import requests
import datetime
import jwt
from rest_framework import viewsets, mixins, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from openai import OpenAI
from django.db.models import Sum, F

from api.custom_permissions import IsTeacher

from api.models import Meeting, ClassMember, Remark, Rating, Feedback, MeetingComment, MeetingPresentor, User

from api.serializers import MeetingSerializer, MeetingCommentSerializer, MeetingCriteriaSerializer, MeetingPresentorSerializer, RatingSerializer, RemarkSerializer, FeedbackSerializer, NoneSerializer

VIDEOSDK_API_ENDPOINT=os.environ.get('VIDEOSDK_API_ENDPOINT')

class MeetingsController(viewsets.GenericViewSet,
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    authentication_classes = [JWTAuthentication]

    VIDEOSDK_API_KEY  = os.environ.get('VIDEOSDK_API_KEY')
    VIDEOSDK_SECRET_KEY = os.environ.get('VIDEOSDK_SECRET_KEY')

    def get_permissions(self):
        if self.action in ['create','destroy', 'update', 'partial_update','retrieve', 'list', 'join']:
        #     return [permissions.IsAuthenticated(), IsTeacher()]
        # elif self.action in []:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="List all meetings under a classroom.",
        operation_description="GET /meetings",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def list(self, request):
        status_param = request.query_params.get('status', None)
        classroom_param = request.query_params.get('classroom', None)
        
        if classroom_param:
            meeting = Meeting.objects.filter(classroom_id=classroom_param)

        if status_param!="all":
            meeting = Meeting.objects.filter(status=status_param)


        serializer = MeetingSerializer(meeting, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Creates a new comment for the specific meeting.",
        operation_description="POST /meetings/{id}/comments",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingCommentSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def add_comment(self, request, *args, **kwargs):
        meeting = self.get_object()
        
        try:
            commentString = request.data['comment'] 
            classMemberId = request.data['classmember_id'] 
            # get ClassMember instance
            classMember = ClassMember.objects.get(id=classMemberId)

            comment = MeetingComment.objects.create(
                classmember_id=classMember,
                comment=commentString
              )

            comment_serializer = MeetingCommentSerializer(comment)
            meeting.comments.add(comment_serializer.data['id'])
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)

            # if comment_serializer.is_valid():
            # return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ClassMember.DoesNotExist:
            return Response({'details': 'Class member not found'}, status=status.HTTP_404_NOT_FOUND)
            
    @swagger_auto_schema(
        operation_summary="List comments for the specific meeting.",
        operation_description="GET /meetings/{id}/comments",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingCommentSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['GET'])
    def get_comments(self, request, *args, **kwargs):
        meeting = self.get_object()

        comment_serializer = MeetingCommentSerializer(meeting.comments.all(), many=True)

        return Response(comment_serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Add a new pitch as presentors for the specific meeting.",
        operation_description="POST /meetings/{id}/presentors/",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingPresentorSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def add_presentor(self, request, *args, **kwargs):
        meeting = self.get_object()

        request.data['meeting_id'] = meeting.id

        presentor_serializer = MeetingPresentorSerializer(data=request.data)

        if presentor_serializer.is_valid():
            presentor_serializer.save()
            meeting.presentors.add(presentor_serializer.data['id'])
            meeting.save()
            return Response(presentor_serializer.data, status=status.HTTP_201_CREATED)
        return Response(presentor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    @swagger_auto_schema(
        operation_summary="List presentors for the specific meeting.",
        operation_description="GET /meetings/{id}/presentors/",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingPresentorSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['GET'])
    def get_presentors(self, request, *args, **kwargs):
        meeting = self.get_object()

        presentor_serializer = MeetingPresentorSerializer(meeting.presentors.all(), many=True)

        return Response(presentor_serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Add a new criterias for the specific meeting.",
        operation_description="POST /meetings/{id}/criterias/",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingCriteriaSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def add_criteria(self, request, *args, **kwargs):
        meeting = self.get_object()

        request.data['meeting_id'] = meeting.id

        criteria_serializer = MeetingCriteriaSerializer(data=request.data)

        if criteria_serializer.is_valid():
            criteria_serializer.save()
            meeting.criterias.add(criteria_serializer.data['id'])
            meeting.save()
            return Response(criteria_serializer.data, status=status.HTTP_201_CREATED)
        return Response(criteria_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    @swagger_auto_schema(
        operation_summary="List criterias for the specific meeting.",
        operation_description="GET /meetings/{id}/criterias/",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingPresentorSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['GET'])
    def get_criterias(self, request, *args, **kwargs):
        meeting = self.get_object()

        meeting_criteria_id = MeetingCriteriaSerializer(meeting.criterias.all(), many=True)

        return Response(meeting_criteria_id.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Update is_rate_open to true to the presentors for the specific meeting.",
        operation_description="POST /meetings/{id}/open_rating_to_pitch/",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', NoneSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def open_rating_to_pitch(self, request, *args, **kwargs):
        meeting = self.get_object()
        presentor = request.data.get('presentor')

        for p in MeetingPresentor.objects.filter(meeting_id=meeting.id):
            p.is_rate_open = False
            p.save()

        selected_presentor = meeting.presentors.get(id=presentor)

        selected_presentor.is_rate_open = True
        selected_presentor.save()

        return Response({'message': f'Rating is open for the selected presentor'}, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="Add a score/rating to the presentors for the specific meeting.",
        operation_description="POST /meetings/{id}/add_rating_to_pitch/",
        request_body=RatingSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', RatingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def add_rating_to_pitch(self, request, *args, **kwargs):
        meeting = self.get_object()

        request.data['meeting_id'] = meeting.id

        rating_serializer = RatingSerializer(data=request.data)

        if rating_serializer.is_valid():
            rating_serializer.save()
            return Response(rating_serializer.data, status=status.HTTP_201_CREATED)
        return Response(rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Update a score/rating to the presentors for the specific meeting.",
        operation_description="POST /meetings/{id}/update_rating_to_pitch/",
        request_body=RatingSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', RatingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['PUT'])
    def update_rating_to_pitch(self, request, *args, **kwargs):
        meeting = self.get_object()
        rating_id = request.data.get('id')
        pitch = request.data.get('pitch_id')
        new_rating = request.data.get('rating')
        meeting_criteria_id = request.data.get('meeting_criteria_id')

        rating= Rating.objects.get(id=rating_id)

        rating.rating = new_rating

        rating.save()

        return Response(RatingSerializer(rating).data, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(
        operation_summary="Add a reamark to the presentors for the specific meeting.",
        operation_description="POST /meetings/{id}/add_remark_to_pitch/",
        request_body=RemarkSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', RemarkSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def add_remark_to_pitch(self, request, *args, **kwargs):
        meeting = self.get_object()

        request.data['meeting_id'] = meeting.id

        rating_serializer = RemarkSerializer(data=request.data)

        if rating_serializer.is_valid():
            rating_serializer.save()
            return Response(rating_serializer.data, status=status.HTTP_201_CREATED)
        return Response(rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Update a remark to the presentors for the specific meeting.",
        operation_description="POST /meetings/{id}/update_remark_to_pitch/",
        request_body=RemarkSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', RemarkSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['PUT'])
    def update_remark_to_pitch(self, request, *args, **kwargs):
        meeting = self.get_object()

        pitch = request.data.get('pitch_id')
        new_remark = request.data.get('remark')

        remark= Remark.objects.get(meeting_id=meeting.id, pitch_id=pitch)

        remark.remark = new_remark

        remark.save()

        return Response(RemarkSerializer(remark).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Summarize the reamarks of the presentors for the specific meeting.",
        operation_description="POST /meetings/{id}/summarize_presentors_remarks/",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingPresentorSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def summarize_presentors_remarks(self, request, *args, **kwargs):
        meeting = self.get_object()

        presentors = MeetingPresentorSerializer(meeting.presentors.all(), many=True).data

        for presentor in presentors:
            remarks = RemarkSerializer(Remark.objects.filter(meeting_id=meeting.id, pitch_id=presentor['pitch_id']), many=True).data    
            prompt = '\n\n'.join(remark['remark'] for remark in remarks if 'remark' in remark)

            complete_prompt = f'Please provide a concise summary of the remarks. Highlight key strengths and areas for improvement mentioned by each evaluator. Provide it into a single paragraph.{prompt}'

            client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))
            openai_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    'role': 'user', 'content': complete_prompt
                }],
                temperature=0
            )

            feedback = {
                'pitch_id': presentor['pitch_id'],
                'meeting_id': meeting.id,
                'feedback': openai_response.choices[0].message.content
            }

            feedback_serializer = FeedbackSerializer(data=feedback)

            if not feedback_serializer.is_valid():
                return Response(feedback_serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
    
            feedback_serializer.save()
            presentor['feedback'] = feedback_serializer.data

            return Response(presentors, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="List all of the rating to the presentors for the specific meeting.",
        operation_description="GET /meetings/{id}/rating_history/",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingPresentorSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['GET'])
    def get_rating_history(self, request, *args, **kwargs):
        meeting = self.get_object()
        
        ratings = Rating.objects.filter(meeting_id=meeting.id)
        serializedRatings = RatingSerializer(ratings, many=True).data

        return Response(serializedRatings, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="List all of the remarks to the presentors for the specific meeting.",
        operation_description="GET /meetings/{id}/remark_history/",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingPresentorSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['GET'])
    def get_remark_history(self, request, *args, **kwargs):
        meeting = self.get_object()

        remarks = Remark.objects.filter(meeting_id=meeting.id)
        serializedRemarks = RemarkSerializer(remarks, many=True).data
        return Response(serializedRemarks, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="List all of the feedbacks to the presentors for the specific meeting.",
        operation_description="GET /meetings/{id}/feedback_history/",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingPresentorSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['GET'])
    def get_feedback_history(self, request, *args, **kwargs):
        meeting = self.get_object()

        feedbacks = Feedback.objects.filter(meeting_id=meeting.id)
        serializedFeedbacks = FeedbackSerializer(feedbacks, many=True).data
        return Response(serializedFeedbacks, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Start Meeting.",
        operation_description="POST /meetings/{id}/start_meeting",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def start_meeting(self, request, *args, **kwargs):
        meeting = self.get_object()

        meeting.status = "in_progress"

        # video sdk
        expiration_in_seconds = 600
        expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)
        token = jwt.encode(payload={
            'exp': expiration,
            'apikey': self.VIDEOSDK_API_KEY,
            'permissions': ['allow_join', 'allow_mod'],
        }, key=self.VIDEOSDK_SECRET_KEY, algorithm="HS256")

        res = requests.post(f'{VIDEOSDK_API_ENDPOINT}/api/meetings',
                            headers={'Authorization': token})
        meeting.video = res.json()['meetingId']
        meeting.token = token
        meeting.save()

        meeting_data = MeetingSerializer(meeting).data

        meeting_data['token'] = token

        return Response(meeting_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Join Meeting.",
        operation_description="POST /meetings/{id}/join_meeting",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def join_meeting(self, request, *args, **kwargs):
        meeting = self.get_object()

        # video sdk
        expiration_in_seconds = 600
        expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)
        token = jwt.encode(payload={
            'exp': expiration,
            'apikey': self.VIDEOSDK_API_KEY,
            'permissions': ['allow_join', 'allow_mod'],
        }, key=self.VIDEOSDK_SECRET_KEY, algorithm="HS256")

        # res = requests.post(f'{VIDEOSDK_API_ENDPOINT}/api/meetings/{meeting.video}',
        #                     headers={'Authorization': token})

        meeting_data = MeetingSerializer(meeting).data

        meeting_data['token'] = token

        return Response(meeting_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="End Meeting.",
        operation_description="PUT /meetings/{id}/end_meeting",
        request_body=NoneSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def end_meeting(self, request, *args, **kwargs):
        meeting = self.get_object()

        meeting.status = "completed"
        meeting.video = None
        meeting.save()

        return Response(MeetingSerializer(meeting).data, status=status.HTTP_200_OK)

    swagger_auto_schema(
        operation_summary="Invite User to Meeting.",
        operation_description="POST /meetings/{id}/invite",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=True, methods=['POST'])
    def invite(self, request, *args, **kwargs):
        meeting = self.get_object()
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            meeting.invited_users.add(user)
            meeting.save()
            return Response({"message": f"{email} invited successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    swagger_auto_schema(
        operation_summary="Get Invited Meetings.",
        operation_description="GET /meetings/get_invited_meetings/{email}",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=False, methods=['GET'])
    def get_invited_meetings(self, request):
        email = request.query_params.get('email')  
        if not email:
            return Response({"error": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        #Get meetings where the user is an invited participant
        meetings = Meeting.objects.filter(invited_users=user).exclude(status='completed')

        if not meetings.exists():
            return Response({"message": "No meetings found for this user."}, status=status.HTTP_404_NOT_FOUND)

        #Collect meeting IDs and statuses
        #Can modify this and add more important values to be returned
        #This is the current return, id and classroom_id is needed to join a meeting.
        meeting_data = meetings.values('id', 'status', 'classroom_id', 'name')

        return Response({"meetings": list(meeting_data)}, status=status.HTTP_200_OK)

    swagger_auto_schema(
        operation_summary="Validate User Email Invite.",
        operation_description="POST /meetings/validate_email",
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', MeetingSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(detail=False, methods=['POST'])
    def validate_email(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        exists = User.objects.filter(email=email).exists()
        if exists:
            return Response({"message": "Email exists"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)