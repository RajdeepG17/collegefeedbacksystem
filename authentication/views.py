from django.shortcuts import render, redirect
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from college_feedback_system.utils.security import (
    validate_password_strength, 
    sanitize_input, 
    generate_password_reset_token, 
    send_password_reset_email, 
    validate_reset_token,
    log_security_event
)
from college_feedback_system.utils.login_tracker import track_login_attempt, get_remaining_attempts
from college_feedback_system.utils.logging import logger
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
from .forms import LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
        
        # Create user
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"User registered successfully: {user.email}")

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
            logger.info(f"Password reset requested for {user.email}")
            # In a real application, you would send an email here
            return Response({'message': 'Password reset email sent'})
        except User.DoesNotExist:
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            # For security reasons, don't expose that the user doesn't exist
            return Response({'message': 'Password reset email sent'})

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
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            logger.info(f"User logged out: {request.user.email}")
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
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
                logger.warning(f"Failed login attempt for user: {email}")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(user)
            logger.info(f"User logged in successfully: {email}")

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type
                }
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class PasswordChangeView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            old_password = serializer.validated_data.get('old_password')
            if not user.check_password(old_password):
                return Response(
                    {'old_password': 'Wrong password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            
            # Update token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'detail': 'Password updated successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    """
    View for user registration with security enhancements
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        try:
            # Sanitize input
            data = sanitize_input(request.data)
            
            # Check if user already exists and can log in
            email = data.get('email', '')
            password = data.get('password', '')
            
            if User.objects.filter(email=email).exists():
                # The user already exists, try to authenticate
                user = authenticate(username=email, password=password)
                
                if user and user.is_active:
                    # The user exists and can log in with these credentials
                    # This means they're trying to register an account that already exists
                    # and they know the password - so we can just return a success
                    refresh = RefreshToken.for_user(user)
                    
                    logger.info(
                        "existing_user_registration_success",
                        extra={"email": email}
                    )
                    
                    # Return success response as if the user was just created
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': UserProfileSerializer(user).data,
                        'message': 'You already have an account with these credentials. Login successful.'
                    }, status=status.HTTP_200_OK)
            
            # Validate password strength
            try:
                validate_password_strength(password)
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process registration
            serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                
                logger.info(
                    "registration_successful",
                    extra={"email": data.get('email')}
                )
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': serializer.data,
                    'message': 'Registration successful'
                }, status=status.HTTP_201_CREATED)
            else:
                logger.warning(
                    "registration_validation_failed",
                    extra={"errors": str(serializer.errors)}
                )
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(
                "registration_error",
                extra={"error": str(e)}
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

# Add a simple login view with AllowAny permission
class SimpleLoginView(APIView):
    """Simple login view that works with both username and email"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        # Get credentials from request
        email = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Please provide both email/username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to authenticate with both email and username
        user = None
        
        # First try direct authentication
        user = authenticate(username=email, password=password)
        
        # If not found, try to find by email and authenticate
        if not user:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user and user.is_active:
            # Generate token
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Return success response with token and user data
            return Response({
                'access': str(access),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': getattr(user, 'user_type', 'student')
                }
            })
        
        # Return error response
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

def login_view(request):
    """
    View for handling user login
    """
    # If user is already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.is_student():
            return redirect('student_dashboard')
        else:
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            
            # Redirect based on user type
            if user.is_student():
                return redirect('student_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            # Authentication failed
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')

def register_view(request):
    """
    View for student registration
    """
    # If user is already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.is_student():
            return redirect('student_dashboard')
        else:
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'accounts/register.html')
        
        # Create new user (student)
        try:
            # Parse the name into first and last name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='student'
            )
            
            # Log the user in
            login(request, user)
            
            # Redirect to student dashboard
            messages.success(request, 'Registration successful! Welcome to College Feedback System.')
            return redirect('student_dashboard')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'accounts/register.html')

@login_required
def logout_view(request):
    """
    View for user logout
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def student_dashboard(request):
    """
    Dashboard view for students
    """
    if not request.user.is_student():
        return redirect('admin_dashboard')
    
    # Get the student's feedbacks
    feedbacks = request.user.submitted_feedbacks.all().order_by('-created_at')
    
    context = {
        'feedbacks': feedbacks
    }
    
    return render(request, 'accounts/student_dashboard.html', context)

@login_required
def admin_dashboard(request):
    """
    Dashboard view for admins
    """
    if request.user.is_student():
        return redirect('student_dashboard')
    
    # Get feedbacks assigned to this admin
    feedbacks = request.user.assigned_feedbacks.all().order_by('-created_at')
    
    # Count pending and resolved feedbacks
    pending_count = feedbacks.filter(status='pending').count()
    resolved_count = feedbacks.filter(status='resolved').count()
    
    context = {
        'feedbacks': feedbacks,
        'pending_count': pending_count,
        'resolved_count': resolved_count
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)
