from rest_framework.permissions import IsAuthenticated, AllowAny
from ..services.jwt_authentication import JWTAuthentication, JWTHasAnyScope
from rest_framework.views import APIView

class BaseAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, JWTHasAnyScope]
    required_scopes = ['admin', 'write']  

class PublicAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]