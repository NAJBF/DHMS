from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    CurrentUserSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user data with tokens."""
    
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        tags=['auth'],
        summary='Login',
        description='Authenticate user and get JWT tokens with user data.',
        responses={
            200: OpenApiResponse(description='Login successful'),
            401: OpenApiResponse(description='Invalid credentials'),
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                'success': True,
                'token': response.data.get('access'),
                'refresh': response.data.get('refresh'),
                'user': response.data.get('user'),
            })
        return response


class RegisterView(generics.CreateAPIView):
    """User registration view."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['auth'],
        summary='Register',
        description='Register a new user account.',
        responses={
            201: OpenApiResponse(description='Registration successful'),
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'full_name': user.full_name,
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Logout view that blacklists the refresh token."""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['auth'],
        summary='Logout',
        description='Logout user and blacklist the refresh token.',
        responses={
            200: OpenApiResponse(description='Logout successful'),
            400: OpenApiResponse(description='Invalid token'),
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            })
        except Exception:
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            })


class CurrentUserView(APIView):
    """Get current authenticated user info."""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['auth'],
        summary='Get Current User',
        description='Get the currently authenticated user information with permissions.',
        responses={
            200: CurrentUserSerializer,
        }
    )
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        })
