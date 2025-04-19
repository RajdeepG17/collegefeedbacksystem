from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from utils.security import (
    validate_password_strength, 
    sanitize_input, 
    generate_password_reset_token, 
    send_password_reset_email, 
    validate_reset_token,
    log_security_event
)
from utils.login_tracker import track_login_attempt, get_remaining_attempts
from utils.logging import logger
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    UserLoginSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses our custom serializer"""
    serializer_class = CustomTokenObtainPairSerializer

class UserRegistrationView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate password strength
        password = serializer.validated_data.get('password')
        if not validate_password_strength(password):
            return Response(
                {'error': 'Password does not meet strength requirements'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        log_security_event('user_registration', {
            'user_id': user.id,
            'email': user.email
        })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    """View for changing password"""
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class PasswordResetView(generics.CreateAPIView):
    """View for requesting password reset"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Generate reset token and send email
            # Implementation depends on your email service
            log_security_event('password_reset_request', {
                'user_id': user.id,
                'email': user.email
            })
            return Response({'message': 'Password reset email sent'})
        except User.DoesNotExist:
            return Response(
                {'error': 'No user found with this email'},
                status=status.HTTP_404_NOT_FOUND
            )

class PasswordResetConfirmView(generics.GenericAPIView):
    """View for confirming password reset"""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, serializer.validated_data['token']):
            return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """View for user logout"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # Add token to blacklist if using JWT
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                track_login_attempt(email, False)
                remaining = get_remaining_attempts(email)
                return Response(
                    {'error': 'Invalid credentials', 'remaining_attempts': remaining},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            track_login_attempt(email, True)
            refresh = RefreshToken.for_user(user)

            log_security_event('user_login', {
                'user_id': user.id,
                'email': user.email
            })

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.profile.role if hasattr(user, 'profile') else None
                }
            })

        except User.DoesNotExist:
            track_login_attempt(email, False)
            remaining = get_remaining_attempts(email)
            return Response(
                {'error': 'Invalid credentials', 'remaining_attempts': remaining},
                status=status.HTTP_401_UNAUTHORIZED
            )

class PasswordChangeView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_password = serializer.validated_data['new_password']
        if not validate_password_strength(new_password):
            return Response(
                {'error': 'New password does not meet strength requirements'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        log_security_event('password_change', {
            'user_id': user.id,
            'email': user.email
        })

        return Response({'message': 'Password changed successfully'})

class RegisterView(generics.CreateAPIView):
    """
    View for user registration with security enhancements
    """
    def post(self, request):
        try:
            # Sanitize input
            data = sanitize_input(request.data)
            
            # Validate password strength
            try:
                validate_password_strength(data.get('password', ''))
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Your registration logic here
            # ...

            logger.info(
                "registration_successful",
                email=data.get('email')
            )
            
            return Response(
                {'message': 'Registration successful'},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(
                "registration_error",
                error=str(e),
                exc_info=True
            )
            return Response(
                {'error': 'An error occurred during registration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ForgotPasswordView(APIView):
    """
    Basic forgot password view
    """
    def post(self, request):
        try:
            email = sanitize_input(request.data.get('email', ''))
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Don't reveal whether user exists
                return Response(
                    {'message': 'If an account exists with this email, you will receive a password reset link.'},
                    status=status.HTTP_200_OK
                )

            # Generate reset token
            uid, token = generate_password_reset_token(user)
            
            # Create reset URL
            reset_url = f"{settings.SITE_URL}/reset-password/{uid}/{token}/"
            
            # Send reset email
            if send_password_reset_email(user, reset_url):
                return Response(
                    {'message': 'Password reset link has been sent to your email.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Failed to send password reset email.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(
                "forgot_password_error",
                error=str(e),
                exc_info=True
            )
            return Response(
                {'error': 'An error occurred while processing your request.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResetPasswordView(APIView):
    """
    Basic password reset view
    """
    def post(self, request, uid, token):
        try:
            # Get user from uid
            try:
                user = User.objects.get(pk=uid)
            except (User.DoesNotExist, ValueError):
                return Response(
                    {'error': 'Invalid reset link.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate token
            if not validate_reset_token(user, token):
                return Response(
                    {'error': 'Invalid or expired reset link.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get and validate new password
            new_password = sanitize_input(request.data.get('password', ''))
            try:
                validate_password_strength(new_password)
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(new_password)
            user.save()

            logger.info(
                "password_reset_successful",
                user=user.email
            )

            return Response(
                {'message': 'Password has been reset successfully.'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(
                "password_reset_error",
                error=str(e),
                exc_info=True
            )
            return Response(
                {'error': 'An error occurred while resetting your password.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserListView(generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset
