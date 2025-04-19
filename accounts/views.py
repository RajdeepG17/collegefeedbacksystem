from django.contrib.auth import get_user_model, login, logout, authenticate
from rest_framework import status, permissions, viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    ChangePasswordSerializer, AdminUserSerializer
)

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    """Permission class to check if user is admin"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['admin', 'superadmin']

class UserRegistrationView(generics.CreateAPIView):
    """View for user registration"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "message": "User created successfully",
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """View for user login"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response(
                    {'error': 'Please provide both email and password'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use username=email since Django's authenticate expects username
            user = authenticate(username=email, password=password)
            
            if user is not None and user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                    'message': 'Login successful'
                })
            
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print(f"Login error: {str(e)}")  # Add debug print
            return Response(
                {'error': 'An error occurred during login. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    """View for user logout"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Only admins can see all users
        if user.user_type in ['admin', 'superadmin']:
            return User.objects.all()
        # Regular users can only see their own profile
        return User.objects.filter(id=user.id)
    
    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            return [IsAdminUser()]
        # Allow users to view and update their own profile
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change password endpoint"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'error': 'Current password is incorrect'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({'message': 'Password changed successfully'})
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def admins(self, request):
        """Get list of admin users by category"""
        admins = User.objects.filter(user_type='admin', is_active=True)
        serializer = AdminUserSerializer(admins, many=True)
        return Response(serializer.data)