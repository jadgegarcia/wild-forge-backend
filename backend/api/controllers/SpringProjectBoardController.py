import json
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from api.serializers import SpringProjectBoardSerializer, SpringProjectSerializer
from api.models import SpringProject, SpringProjectBoard, SpringBoardTemplate, Team, TeamMember, ActivityComment, Activity, ActivityCriteriaRelation,ActivityCriteria,SpringBoardTemplate
import requests
from django.db.models import Max
from django.conf import settings
import os
from openai import OpenAI
import google.generativeai as genai
from django.core.serializers import serialize
import json
from django.utils.timezone import now

class CreateProjectBoard(generics.CreateAPIView):
    serializer_class = SpringProjectBoardSerializer

    def perform_create(self, serializer, data):
        serializer.save(**data)

    def update_project_score(self, project, add_score):
        project.score += add_score
        project.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = {}
        highest_board_id = SpringProjectBoard.objects.aggregate(Max('board_id'))[
            'board_id__max']
        new_board_id = highest_board_id + 1 if highest_board_id is not None else 1
        activity_id = request.data.get('activity_id', None)
        activity_instance = Activity.objects.get(id= activity_id)
        activity_criteria_list = ActivityCriteriaRelation.objects.filter(activity_id = activity_instance.id)
        activity_criteria_json = serialize('json', activity_criteria_list)
        parsed_json = json.loads(activity_criteria_json)
        result_json = {}

        template_instance = SpringBoardTemplate.objects.filter(title = activity_instance.title).first()
        if not template_instance:
            template_instance = SpringBoardTemplate.objects.create(
                title=activity_instance.title,
                content="",
                rules = activity_instance.instruction,
                description = activity_instance.description,
                date_created = now()
            )
        for item in parsed_json:
            try:
                # Fetch activity_criteria ID and use it to get the name
                activity_criteria_id = item["fields"]["activity_criteria"]
                activity_criteria_name = ActivityCriteria.objects.get(pk=activity_criteria_id).name
                
                # Store the feedback data in the required format
                result_json[activity_criteria_name] = {
                    "score": item["fields"]["rating"],
                    "description": item["fields"]["activity_criteria_feedback"]
                }
            except Exception as e:
                print(f"Error processing item {item}: {e}")
        result_json_string = json.dumps(result_json, indent=4)
        criteria_feedback = result_json_string
        print("Activity Name: ", activity_instance.title)
        prompt = (
            f"Please analyze the following data: {criteria_feedback}. "
            f"\nJust basing on each Criteria which has a Score and a description."
            f"\nBased on the scores and description, give an overall feedback."
            f"\nAlso give a recommendation that can be used to improve."
            f"\nBe critical and practical when rating. "
            f"Include at least 2 specific sentences of advice for improvements (Recommendations) and (Feedback). "
            f"2 sentences of feedback on how the data is presented and structured, and what can be done to improve those aspects (Feedback) for each of the above aspects. "
            f"Also provide calculate the average score: "
            f"The output should be in the following JSON format: "
            f"Ensure the feedback and recommenddation is only 2-3 sentences: "
            f"\n'feedback': 'feedback result', 'recommendation': 'recommendation result', 'score': average_score(int) "
            f"Ensure a fair and balanced assessment for each aspect. Explain in detail and use '\n' for new lines."
        )
        
        # client = OpenAI(api_key=os.environ.get("OPENAI_KEY", "")) 
        # message = [
        #     {"role": "user", "content": prompt}
        # ]
        genai.configure(api_key="AIzaSyD177Z-9JXRbuFqL4CsZm2rBAckVnVc-YI")
        model = genai.GenerativeModel('gemini-1.5-pro-latest',generation_config={"response_mime_type": "application/json"})

        try:
            # response = client.chat.completions.create(
            #     model="gpt-3.5-turbo", messages=message, temperature=0, max_tokens=1050
            # )
            response = model.generate_content(prompt)

            if response:
                try:
                    choices = response.text
                    # first_choice_content = response.choices[0].message.content

                    if choices:
                        # gpt_response = first_choice_content
                        json_response = json.loads(response.text)
                        print("json response")
                        print(json_response)
                        recommendation = json_response.get('recommendation', "")
                        feedback = json_response.get('feedback', "")
                        score = activity_instance.evaluation/activity_instance.total_score * 10
                        print("Score:" , score)

                        print("Recommendation:", recommendation)
                        print("Feedback:", feedback)
                        title = request.data.get('title', "")
                        project_id_id = request.data.get('project_id', None)

                        data = {
                            'title': title,
                            'recommendation': recommendation,
                            'feedback': feedback,
                            'project_id': SpringProject.objects.get(id=project_id_id),
                            'board_id': new_board_id,
                            'criteria_feedback': criteria_feedback,
                            'score': score,
                            'activity_id': activity_id,
                            'template_id': template_instance.id
                        }

                        project_instance = SpringProject.objects.get(
                            id=project_id_id)
                        add_score = (
                            score
                        )
                        self.update_project_score(
                            project_instance, add_score)

                    else:
                        print("No response content or choices found.")
                except json.JSONDecodeError as json_error:
                    return Response({"error": f"Error decoding JSON response: {json_error}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": response.text}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            data = {}
        print("DATA NI:")
        print(data)
        if serializer.is_valid():
            self.perform_create(serializer, data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("serializer error: ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetProjectBoards(generics.ListAPIView):
    serializer_class = SpringProjectBoardSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        queryset = SpringProjectBoard.objects.filter(project_id_id=project_id)
        
        # queryset = SpringProjectBoard.objects.filter(project_id_id=project_id).values(
        #     'template_id').annotate(
        #         latest_id=Max('id'),
        # ).values(
        #         'latest_id',
        # )
        return SpringProjectBoard.objects.filter(id__in=queryset)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetVersionProjectBoards(generics.ListAPIView):
    serializer_class = SpringProjectBoardSerializer
    queryset = SpringProjectBoard.objects.all()

    def get(self, request, *args, **kwargs):
        projectboard_id = self.kwargs.get('projectboard_id')

        try:
            projectboard = SpringProjectBoard.objects.get(id=projectboard_id)
            template_id = projectboard.template_id
            board_id = projectboard.board_id

            related_projectboards = SpringProjectBoard.objects.filter(
                template_id=template_id, board_id=board_id)

            related_projectboards = related_projectboards.order_by(
                '-date_created')

            serializer = SpringProjectBoardSerializer(
                related_projectboards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SpringProjectBoard.DoesNotExist:
            return Response({"error": "ProjectBoard not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetProjectBoardById(generics.ListAPIView):
    serializer_class = SpringProjectBoardSerializer
    queryset = SpringProjectBoard.objects.all()

    def get(self, request, *args, **kwargs):
        projectboard_id = self.kwargs.get('projectboard_id')

        try:
            projectboard = SpringProjectBoard.objects.get(id=projectboard_id)
            serializer = SpringProjectBoardSerializer(projectboard)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SpringProjectBoard.DoesNotExist:
            return Response({"error": "ProjectBoards not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateBoard(generics.CreateAPIView):
    serializer_class = SpringProjectBoardSerializer

    def update_project_score(self, project, subtract_score, new_score):
        project.score -= subtract_score
        project.score += new_score
        project.save()

    def create(self, request, *args, **kwargs):
        data = request.data
        project_board_id = kwargs.get('projectboard_id')

        try:
            project_board = SpringProjectBoard.objects.get(id=project_board_id)

            subtract_score = (project_board.score)

            criteria_feedback = request.data.get('criteria_feedback', None)
            activity_id = request.data.get('activity_id', None)

            prompt = (
                f"Please analyze the following data: {criteria_feedback}. "
                f"\nJust basing on each Criteria which has a Score and a description."
                f"\nBased on the scores and description, give an overall feedback."
                f"\nAlso give a recommendation that can be used to improve."
                f"\nBe critical and practical when rating. "
                f"Include at least 2 specific sentences of advice for improvements (Recommendations) and (Feedback). "
                f"2 sentences of feedback on how the data is presented and structured, and what can be done to improve those aspects (Feedback) for each of the above aspects. "
                f"Also provide calculate the average score: "
                f"The output should be in the following JSON format: "
                f"\n'feedback': 'feedback result', 'recommendation': 'recommendation result', 'score': average_score(int) "
                f"Ensure a fair and balanced assessment for each aspect. Explain in detail and use '\n' for new lines."
            )
            genai.configure(api_key="AIzaSyC3Zs-NV83dd6p9WgAIeT4iwYZOWHpsihw")
            model = genai.GenerativeModel('gemini-1.5-pro-latest',generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)

            # client = OpenAI(api_key=os.environ.get("OPENAI_KEY", ""))
            # message = [
            #     {"role": "user", "content": prompt}
            # ]
            # response = client.chat.completions.create(
            #     model="gpt-3.5-turbo", messages=message, temperature=0, max_tokens=1050
            # )
            if response:
                try:
                    choices = response
                    # first_choice_content = response.choices[0].message.content
                    if choices:
                        # gpt_response = first_choice_content
                        json_response = json.loads(response.text)
                        print(json_response)
                        recommendation = json_response.get('recommendation', "")
                        feedback = json_response.get('feedback', "")
                        score = json_response.get("score", 0)
                        print("Score:" , score)

                        print("Recommendation:", recommendation)
                        print("Feedback:", feedback)
                                            
                        data = {
                            'title': data.get('title', ''),
                            'recommendation': recommendation,
                            'feedback': feedback,
                            'project_id': project_board.project_id,
                            'template_id': project_board.template_id,
                            'board_id': project_board.board_id,
                            'criteria_feedback': criteria_feedback,
                            'score': score,
                            'activity_id': activity_id
                        }

                        new_board_instance = SpringProjectBoard(**data)
                        new_board_instance.save()

                        project_instance = SpringProject.objects.get(
                            id=project_board.project_id.id)

                        new_score = (score)
                        subtract_score = subtract_score

                        self.update_project_score(
                            project_instance, subtract_score, new_score)

                    else:
                        return Response({"error": "No response content or choices found"}, status=status.HTTP_400_BAD_REQUEST)
                except json.JSONDecodeError as json_error:
                    return Response({"error": f"Error decoding JSON response: {json_error}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": response.text}, status=status.HTTP_400_BAD_REQUEST)

        except SpringProjectBoard.DoesNotExist:
            return Response({"error": "ProjectBoard not found"}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"id": new_board_instance.id}, status=status.HTTP_201_CREATED)


class DeleteProjectBoard(generics.DestroyAPIView):
    queryset = SpringProjectBoard.objects.all()
    serializer_class = SpringProjectBoardSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            subtract_score = (
                (instance.score * 0.4)
            )
            instance.project_id.score -= subtract_score
            instance.project_id.save()
            SpringProjectBoard.objects.filter(
                board_id=instance.board_id).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except SpringProjectBoard.DoesNotExist:
            return Response({"error": "ProjectBoard not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
