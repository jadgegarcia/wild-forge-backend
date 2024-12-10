from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db import transaction
from api.custom_permissions import IsTeacher, IsModerator

from api.models import Activity
from api.models import ActivityTemplate
from api.models import ClassRoom
from api.models import Team
from api.models import ActivityWorkAttachment
from api.models import ActivityCriteria
from api.models import ActivityComment
from api.models import ClassMember
from api.models import User
from api.models import ActivityCriteriaRelation
from api.models import ActivityGeminiSettings
from api.models import SpringProject

from api.serializers import ActivityWorkAttachmentSerializer
from api.serializers import ActivitySerializer
from api.serializers import ActivityTemplateSerializer
from api.serializers import ActivityCreateFromTemplateSerializer
from api.serializers import ClassRoomSerializer
from api.serializers import TeamSerializer
from api.serializers import CriteriaSerializer

import requests
import traceback
import pymupdf # type: ignore
import os
import textwrap
from PIL import Image
import re

import os
import textwrap
from datetime import timedelta, datetime
from django.utils import timezone
import typing_extensions as typing
from IPython.core.display import Markdown
from PIL import Image
import google.generativeai as genai

import json



class ActivityController(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    authentication_classes = [JWTAuthentication]
    #AIzaSyBzwUqIePVR3UJWhkLWkVHQunP7ZRogr0k
    #AIzaSyCN0cmESuQIO_WA6pFeYkGlE0veJVhCW94
    #AIzaSyAP5-SgR3o2jI45MQ8ZD9Y8AhEGn-_yu0A
    # API_KEY = "AIzaSyBzwUqIePVR3UJWhkLWkVHQunP7ZRogr0k"
    # genai.configure(api_key=API_KEY)
    API_KEY = ActivityGeminiSettings.objects.first()
    genai.configure(api_key=API_KEY.api_key)
    print(API_KEY.api_key)
    

    # for m in genai.list_models():
    #     if 'generateContent' in m.supported_generation_methods:
    #         print(m.name)

    response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "criteria_name": {"type": "STRING"},
                "rating": {"type": "INTEGER"},
                "feedback": {"type": "STRING"},
            },
            "required": ["criteria_name", "rating", "feedback"],
        },
    }

    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": response_schema,
    }
    
    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        #model_name="gemini-1.5-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
    )

        
    def pdf_to_images(pdf_path, output_folder, criteria_with_strictness, activity_instance):
        #D:\TECHNO_SYS\wildforge\techno-systems-main\techno-systems\backend\backend\activity_work_submissions
        #doc = pymupdf.open(pdf_path)  # Attempt to open the PDF
        # doc = pymupdf.open("C:\\Users\\Noel Alemaña\\finaldeploy\\wild-forge\\backend\\backend\\" + pdf_path)
        r = requests.get(pdf_path)
        data = r.content
        doc = pymupdf.Document(stream=data)
        
        #print(f"There are {doc.page_count} Pages")
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            image_path = f"{output_folder}/{doc.name}page_{i + 1}.png"
            pix.save(image_path)
            #print(f"Page {i + 1} converted to image: {image_path}")
        
        img_list = ActivityController.get_images(doc, output_folder, criteria_with_strictness, activity_instance)
        
        #print("PROMPT TEXT: ", img_list)
        
        response = ActivityController.model.generate_content(img_list)
        print("Response Content:", response.text) 
        
        ActivityController.delete_files(doc.page_count,doc.name, output_folder)
        doc.close()
        
        return response.text
    
    

    def delete_files(pageTotal,docName, output_folder):
        for i in range(pageTotal):
            try:

                os.remove(output_folder + f"/{docName}page_{i + 1}.png")
                #print(f"File at {output_folder}/page_{i + 1}.png deleted successfully.")
            except OSError as e:
                print(f"Error: {output_folder}/page_{i + 1}.png - {e.strerror}")

    def get_images(doc, output_folder, criteria_with_strictness, activity_instance):

        image_list = []
        for i in range(doc.page_count):
            image_list.append(f"{output_folder}/{doc.name}page_{i + 1}.png")
        
        images = [
            "You are tasked with analyzing and evaluating a submitted activity, represented by multiple images (pages of a PDF file), according to a set of predefined criteria. " +
            "Your evaluation should focus on the entire file rather than individual pages. " +
            "For each criterion, you must provide a rating on a scale of 0 to 10, along with specific feedback that reflects the degree of compliance with the criterion. " +
            "Additionally, incorporate a strictness level( ranges 1 - 10) that influences the precision and rigor of your evaluation:\n" +
            "\tHigh Strictness(7 - 10): Requires near-perfect adherence to the criterion. Small errors or deviations will significantly reduce the rating.\n" +
            "\tMedium Strictness(5 - 6): Allows for minor mistakes but still demands a high degree of accuracy and completeness.\n" +
            "\tLow Strictness(1 - 4): More forgiving, permitting notable flexibility in meeting the criterion.\n\n" +
            "For each criterion, provide the following:\n" +
            "-Criterion Name\n" +
            "-Rating(A score between 0 and 10, with 0 being the lowest and 10 being the highest.)\n" +
            "-Feedback(Specific comments based on the rating, pointing out strengths, weaknesses, and areas for improvement.)\n" +
            "Your response should include:\n" +
            "Individual ratings and feedback for each criterion.\n" +
            "Adjustments based on the chosen strictness level.\n\n" +
            "Criteria with their respective strictness level:\n" +
            "The Following are the Activity Details." +
            "\nActivity Title: " + activity_instance.title +
            "\nActivity Description: " + activity_instance.description +
            "\nActivity Instructions: " + activity_instance.instruction 
        ]

        # Add the formatted criteria and strictness information
        images += [f"- {criteria} : {strictness}\n" for criteria, strictness in criteria_with_strictness]

        # Add the final section and images to evaluate
        images.append("\n\nImages to Evaluate:\n")


        for i in image_list:
            images.append(Image.open(i))
        #     

        # 
        # 
        # Low Strictness(1 - 4): More forgiving, permitting notable flexibility in meeting the criterion.
        # For each criterion, provide the following:

        # Criterion Name: The aspect of the activity being evaluated (e.g., Completeness, Accuracy, Formatting).
        # Rating: A score between 1 and 5, with 1 being the lowest and 5 being the highest.
        # Feedback: Specific comments based on the rating, pointing out strengths, weaknesses, and areas for improvement.
        # Your response should include:

        # A summary rating for the entire file, considering all criteria.
        # Individual ratings and feedback for each criterion.
        # Adjustments based on the chosen strictness level.


        # print("\n\nPROMPT CHECK")
        # print(images)
        return images
    


    
    def get_permissions(self):
        if self.action in ['create', 'create_from_template', 
                           'destroy', 'add_evaluation', 'delete_evaluation',
                           ]:
            return [permissions.IsAuthenticated(), IsTeacher(), IsModerator()]
        else:
            return [permissions.IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="Creates a new activity",
        operation_description="POST /activities",
        request_body=ActivitySerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', ActivitySerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Invalid or missing data in the request.'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized', message='Unauthorized. Authentication required.'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. One or more teams not found.'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden', message='Forbidden. You do not have permission to access this resource.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            activity_data = serializer.validated_data
            team_ids = request.data.get('team_id', [])
            activityCriteria_ids = request.data.get('activityCriteria_id', [])
            strictness_levels = request.data.get('strictness_levels', [])
            criteria_status = request.data.get('criteria_status', [])
            criteria_feedback = request.data.get('criteria_status', [])

            if team_ids:
                try:
                    teams = Team.objects.filter(pk__in=team_ids)
                    spring_projects = SpringProject.objects.filter(team_id__in=team_ids, is_active=True)

                    #print("Mao ni ang spring projects na active_____________")
                    # Use transaction.atomic to ensure all or nothing behavior
                    with transaction.atomic():
                        activity_instances = []
                        for spring_project in spring_projects:  # Iterating over individual SpringProject instances
                            #print(f"Processing SpringProject: {spring_project}")  # Debugging info
                            # Create a new activity instance for each SpringProject
                            new_activity = Activity.objects.create(
                                classroom_id=activity_data.get('classroom_id'),
                                title=activity_data.get('title'),
                                description=activity_data.get('description'),
                                instruction=activity_data.get('instruction'),
                                submission_status=activity_data.get('submission_status', False),
                                due_date=activity_data.get('due_date'),
                                evaluation=activity_data.get('evaluation'),
                                total_score=activity_data.get('total_score', 100),
                                spring_project=spring_project  # This must be an individual SpringProject instance
                            )
                            new_activity.team_id.add(spring_project.team_id)  # Assuming team_id is ManyToMany
                            # Create ActivityCriteriaRelation instances
                            for criteria_id, strictness in zip(activityCriteria_ids, strictness_levels):
                                activity_criteria_instance = ActivityCriteria.objects.filter(pk=criteria_id).first()
                                if not activity_criteria_instance:
                                    return Response({"error": f"ActivityCriteria with ID {criteria_id} not found"}, status=status.HTTP_404_NOT_FOUND)
                                
                                try:
                                    ActivityCriteriaRelation.objects.create(
                                        activity=new_activity,
                                        activity_criteria=activity_criteria_instance,
                                        strictness=strictness
                                    )
                                except Exception as e:
                                    return Response({"error": f"Failed to create ActivityCriteriaRelation: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


                            activity_instances.append(new_activity)

                    template = ActivityTemplate.objects.create(
                            course_name=activity_data.get('classroom_id').course_name,
                            title=activity_data.get('title'),
                            description=activity_data.get('description'),
                            instructions=activity_data.get('instruction')
                        )

                    activity_serializer = self.get_serializer(activity_instances, many=True)
                    return Response(activity_serializer.data, status=status.HTTP_201_CREATED)
                except Team.DoesNotExist:
                    return Response({'error': 'One or more teams not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Invalid or empty Team IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Lists all activities of a class",
        operation_description="GET /classes/{class_pk}/activities",
       responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivitySerializer(many=True)),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Class ID not provided.'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized', message='Unauthorized. Authentication required.'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden', message='Forbidden. You do not have permission to access this resource.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    def list(self, request, *args, **kwargs):
        class_id = kwargs.get('class_pk', None)

        if class_id:
            try:
                activities = Activity.objects.filter(classroom_id=class_id)
                serializer = self.get_serializer(activities, many=True)
                return Response(serializer.data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Class ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
    operation_summary="Create activity from template",
    operation_description="POST /classes/{class_pk}/activities/from_template",
    request_body=ActivityCreateFromTemplateSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response('Created', ActivitySerializer),
        status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Invalid or missing data in the request.'),
        status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized', message='Unauthorized. Authentication required.'),
        status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. Template or Class not found.'),
        status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
    }
    )
    @action(detail=False, methods=['POST'])
    def create_from_template(self, request, class_pk=None, pk=None):
        class_id = request.data.get('class_id', None)
        template_id = request.data.get('template_id', None)
        team_ids = request.data.get('team_ids', [])
        due_date = request.data.get('due_date', None)
        evaluation = request.data.get('evaluation', None)
        total_score = request.data.get('total_score', None)
        activityCriteria_ids = request.data.get('activityCriteria_id', [])
        strictness_levels = request.data.get('strictness_levels', [])
        

        if template_id is not None and class_pk is not None:
            try:
                class_obj = ClassRoom.objects.get(pk=class_id)
                template = ActivityTemplate.objects.get(pk=template_id)
                spring_projects = SpringProject.objects.filter(team_id__in=team_ids, is_active=True)
                with transaction.atomic():
                    activity_instances = []
                    for spring_project in spring_projects:
                        new_activity = Activity.create_activity_from_template(template)

                        # Update due_date, evaluation, and total_score
                        if due_date:
                                new_activity.due_date = due_date
                            
                        if evaluation:
                                new_activity.evaluation = evaluation
                        if total_score:
                            new_activity.total_score = total_score

                        # Set the class and team for the new activity
                        if class_obj:
                            new_activity.classroom_id = class_obj                    
                        new_activity.spring_project=spring_project
                        new_activity.team_id.add(spring_project.team_id)
                        new_activity.save()
                        for criteria_id, strictness in zip(activityCriteria_ids, strictness_levels):
                            activity_criteria_instance = ActivityCriteria.objects.filter(pk=criteria_id).first()
                            if not activity_criteria_instance:
                                return Response({"error": f"ActivityCriteria with ID {criteria_id} not found"}, status=status.HTTP_404_NOT_FOUND)
                                
                            try:
                                ActivityCriteriaRelation.objects.create(
                                    activity=new_activity,
                                    activity_criteria=activity_criteria_instance,
                                    strictness=strictness,
                                    activity_criteria_status = 1
                                )
                            except Exception as e:
                                return Response({"error": f"Failed to create ActivityCriteriaRelation: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

                            
                        activity_instances.append(new_activity)
                        

                activity_serializer = self.get_serializer(activity_instances, many=True)
                return Response(activity_serializer.data, status=status.HTTP_201_CREATED)
            except (ActivityTemplate.DoesNotExist, ClassRoom.DoesNotExist) as e:
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Template ID or Class ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
            
class TeamActivitiesController(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['add_evaluation', 'delete_evaluation',
                           ]:
            return [permissions.IsAuthenticated(), IsTeacher()]
        else:
            return [permissions.IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="Lists all activities of a team",
        operation_description="GET /classes/{class_pk}/teams/{team_pk}/activities",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivitySerializer(many=True)),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def list(self, request, class_pk=None, team_pk=None):
        try:
            if class_pk is not None and team_pk is not None:
                if not ClassRoom.objects.filter(pk=class_pk).exists():
                    return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
                
                if not Team.objects.filter(pk=team_pk).exists():
                    return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

                activities = Activity.objects.filter(classroom_id=class_pk, team_id=team_pk)
                serializer = self.get_serializer(activities, many=True)
                return Response(serializer.data)

            elif team_pk is None:
                return Response({'error': 'Team ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

            elif class_pk is None:
                return Response({'error': 'Class ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # @swagger_auto_schema(
    #     operation_summary="Lists all submitted activities of a team",
    #     operation_description="GET /classes/{class_pk}/teams/{team_pk}/submitted_activities",
    #     responses={
    #         status.HTTP_200_OK: openapi.Response('OK', ActivitySerializer(many=True)),
    #         status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Either class ID or team ID is missing or invalid.'),
    #         status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized', message='Unauthorized. Authentication required.'),
    #         status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden', message='Forbidden. You do not have permission to access this resource.'),
    #         status.HTTP_404_NOT_FOUND: openapi.Response('Not Found', message='Not Found. Either class or team not found.'),
    #         status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
    #     }
    # )
    # @action(detail=True, methods=['GET'])
    # def submitted_activities(self, request, class_pk=None, team_pk=None):
    #     try:
    #         # Check if both class_id and team_id are provided
    #         if class_pk is not None and team_pk is not None:
    #             # Check if the specified class_id and team_id exist
    #             if not ClassRoom.objects.filter(pk=class_pk).exists():
    #                 return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
                
    #             if not Team.objects.filter(pk=team_pk).exists():
    #                 return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

    #             # Retrieve submitted activities for the specified class_id and team_id
    #             submitted_activities = Activity.objects.filter(classroom_id=class_pk, team_id=team_pk, submission_status=True)
    #             serializer = self.get_serializer(submitted_activities, many=True)
    #             return Response(serializer.data, status=status.HTTP_200_OK)

    #         # Check if team_id is not provided
    #         elif team_pk is None:
    #             return Response({'error': 'Team ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

    #         # Check if class_id is not provided
    #         elif class_pk is None:
    #             return Response({'error': 'Class ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
    operation_summary="Submit or unsubmit an activity",
    operation_description="POST /classes/{class_pk}/teams/{team_pk}/activities/{activity_pk}/submit",
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'submission_status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Submissin status. True for submit, False for unsubmit'),
            },
            required=['evaluation'],
        ),
    responses={
        status.HTTP_200_OK: openapi.Response('OK', ActivitySerializer),
        status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Activity not found or invalid action.'),
        status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized', message='Unauthorized. Authentication required.'),
        status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden', message='Forbidden. You do not have permission to access this resource.'),
        status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
    }
    )
    @action(detail=True, methods=['POST'])
    def submit(self, request, class_pk=None, team_pk=None, pk=None):
        try:
            activity = Activity.objects.get(classroom_id=class_pk, team_id=team_pk, pk=pk)
            activity.submission_status = not activity.submission_status
            activity.save()
            if activity.submission_status is False:
                return Response(status=status.HTTP_200_OK)
            
            attachments = ActivityWorkAttachment.objects.filter(activity_id=activity)
            serializer = ActivityWorkAttachmentSerializer(attachments, many=True)
            today = timezone.localdate()

            if attachments.exists():
                latest_attachment = attachments.order_by('date_created').first()
                last_submission_date = latest_attachment.date_created.date()

                if last_submission_date == today:
                    if activity.submission_attempts >= 3:
                        print("NASOBRAHAN NAKA SUBMIT")
                        return Response({"error": "You have reached the limit of 3 submissions today."})
                        
                    activity.submission_attempts += 1
                    activity.save()
                else:
                    print("WA PA NASOBRAHAN")
                    latest_attachment.date_created = today
                    activity.submission_attempts = 1
                latest_attachment.save()
                activity.save()
            member = ClassMember.objects.get(class_id=activity.classroom_id, role=0)
            theUser = User.objects.get(email=member.user_id)
            

            activity_instance = Activity.objects.get(pk=pk)  # Get an activity instance

            criteria_relations = ActivityCriteriaRelation.objects.filter(activity=activity_instance)

            

            criteria_with_strictness = [
                (relation.activity_criteria.name, relation.strictness)
                for relation in criteria_relations
            ]

            relative_pdf_path = os.getcwd() + os.path.join("/activity_work_submissions")
            #print('submit:' + relative_pdf_path)

            for attachment_data in serializer.data:


                file_attachment = attachment_data['file_attachment']
                #print("Response: asjasjdjkasdhsdajsdajh" )
                response_text = ActivityController.pdf_to_images(
                    file_attachment, 
                    relative_pdf_path, 
                    criteria_with_strictness, activity_instance
                )
            #print("Response: " + response_text)
            data = json.loads(response_text)
                
            with transaction.atomic():
                for item in data:
                    criteria_name = item['criteria_name']
                    feedback = item['feedback']
                    rating = item['rating']

                    try:
                        # Fetch the corresponding ActivityCriteria object
                        activity_criteria = ActivityCriteria.objects.get(name=criteria_name)

                        # Update only if the relation exists, no creation
                        row_update = ActivityCriteriaRelation.objects.filter(
                            activity=activity_instance,
                            activity_criteria=activity_criteria
                        ).update(
                            rating=rating,
                            activity_criteria_feedback=feedback
                        )

                        # if row_update:
                        #     print(f"Updated relation for {criteria_name}")
                        # else:
                        #     print(f"No existing relation found for {criteria_name}, nothing updated.")

                    except ActivityCriteria.DoesNotExist:
                        print(f"ActivityCriteria with name {criteria_name} does not exist.")


   
            
            serializer = self.get_serializer(activity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc()) 
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        operation_summary="Add evaluation for an activity",
        operation_description="POST /classes/{class_pk}/teams/{team_pk}/activities/{activity_pk}/add-evaluation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'evaluation': openapi.Schema(type=openapi.TYPE_INTEGER, description='Evaluation score.'),
            },
            required=['evaluation'],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivitySerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Activity not found, invalid data, or submission status is false.'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized', message='Unauthorized. Authentication required.'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden', message='Forbidden. You do not have permission to access this resource.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    @action(detail=True, methods=['POST'])
    def add_evaluation(self, request, class_pk=None, team_pk=None, pk=None):
        try:
            activity = Activity.objects.get(classroom_id=class_pk, team_id=team_pk, pk=pk)

            if not activity.submission_status:
                return Response({'error': 'Cannot add evaluation for an activity with submission status as false.'}, status=status.HTTP_400_BAD_REQUEST)

            evaluation = request.data.get('evaluation', None)

            if evaluation is not None:
                activity.evaluation = evaluation
                activity.save()
            else:
                return Response({'error': 'Evaluation score not provided'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(activity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @swagger_auto_schema(
        operation_summary="Delete evaluation for an activity",
        operation_description="POST /classes/{class_pk}/teams/{team_pk}/activities/{activity_pk}/delete-evaluation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'evaluation': openapi.Schema(type=openapi.TYPE_INTEGER, description='Evaluation score.'),
            },
            required=['evaluation'],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response('OK', ActivitySerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request', message='Bad Request. Activity not found, invalid data, or submission status is false.'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized', message='Unauthorized. Authentication required.'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden', message='Forbidden. You do not have permission to access this resource.'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error', message='Internal Server Error. An unexpected error occurred.'),
        }
    )
    @action(detail=True, methods=['DELETE'])
    def delete_evaluation(self, request, class_pk=None, team_pk=None, pk=None):
        try:
            activity = Activity.objects.get(classroom_id=class_pk, team_id=team_pk, pk=pk)

            if not activity.submission_status:
                return Response({'error': 'Cannot delete evaluation for an activity with submission status as false.'}, status=status.HTTP_400_BAD_REQUEST)

            activity.evaluation = None
            activity.save()

            serializer = self.get_serializer(activity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

