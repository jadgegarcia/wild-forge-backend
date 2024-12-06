from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from api.serializers import SpringBoardTemplateSerializer
from api.models import SpringBoardTemplate


class CreateTemplate(generics.CreateAPIView):
    serializer_class = SpringBoardTemplateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllTemplate(generics.ListAPIView):
    serializer_class = SpringBoardTemplateSerializer
    queryset = SpringBoardTemplate.objects.all()


# Get Template by id
class GetTemplate(generics.ListAPIView):
    serializer_class = SpringBoardTemplateSerializer
    queryset = SpringBoardTemplate.objects.all()

    def get(self, request, *args, **kwargs):
        template_id = self.kwargs.get('template_id')

        try:
            template = SpringBoardTemplate.objects.get(id=template_id)
            serializer = SpringBoardTemplateSerializer(template)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SpringBoardTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateTemplate(generics.UpdateAPIView):
    serializer_class = SpringBoardTemplateSerializer
    queryset = SpringBoardTemplate.objects.all()

    def update(self, request, *args, **kwargs):
        template_id = self.kwargs.get('template_id')

        try:
            template = SpringBoardTemplate.objects.get(id=template_id)
        except SpringBoardTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SpringBoardTemplateSerializer(template, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTemplate(generics.DestroyAPIView):
    serializer_class = SpringBoardTemplateSerializer
    queryset = SpringBoardTemplate.objects.all()

    def destroy(self, request, *args, **kwargs):
        template_id = self.kwargs.get('template_id')

        try:
            template = SpringBoardTemplate.objects.get(id=template_id)
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SpringBoardTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
