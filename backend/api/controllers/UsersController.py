from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.models import User
from api.serializers import UserSerializer
from api.serializers import LoginSerializer as Login

class UsersController(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        If the action is 'create', allow any user to create a new user.
        If the action is 'retrieve', 'update', 'partial_update', or 'destroy', only allow authenticated users to access.
        otherwise, return 403 Forbidden.
        """

        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()


    @swagger_auto_schema(
        operation_summary="Creates a new user",
        operation_description="POST /users",
        request_body=UserSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Created', UserSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieves a user",
        operation_description="GET /users/{id}",
        responses={
            status.HTTP_200_OK: openapi.Response('OK', UserSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not Found'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # create a POST /users/login endpoint
    @swagger_auto_schema(
        operation_summary="Logs in a user",
        operation_description="POST /users/login",
        request_body=Login,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', UserSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    @action(methods=['POST'], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = Login(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Updates a user",
        operation_description="PUT /users/{id}",
        request_body=UserSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', UserSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    

    @swagger_auto_schema(
        operation_summary="Updates a user partially",
        operation_description="PATCH /users/{id}",
        request_body=UserSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('OK', UserSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Bad Request'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    

    @swagger_auto_schema(
        operation_summary="Deletes a user",
        operation_description="DELETE /users/{id}",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('No Content'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Unauthorized'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal Server Error'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
