from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import AuthTokenObtainPairSerializer

class TokensController(TokenObtainPairView):
    serializer_class = AuthTokenObtainPairSerializer