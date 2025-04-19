from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user data in response"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_type'] = self.user.user_type
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=[('student', 'Student'), ('admin', 'Admin'), ('superadmin', 'Super Admin')],
        required=True
    )
    student_id = serializers.CharField(required=False)
    department = serializers.CharField(required=False)
    year_of_study = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 
                 'user_type', 'department', 'phone_number', 'role', 'student_id', 'year_of_study')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate student-specific fields
        if attrs.get('role') == 'student':
            if not attrs.get('student_id'):
                raise serializers.ValidationError({"student_id": "Student ID is required for student accounts"})
            if not attrs.get('department'):
                raise serializers.ValidationError({"department": "Department is required for student accounts"})
            if not attrs.get('year_of_study'):
                raise serializers.ValidationError({"year_of_study": "Year of study is required for student accounts"})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = validated_data.pop('role')
        
        # Map role to user_type
        validated_data['user_type'] = role
        
        # Create user with basic fields
        password = validated_data.pop('password')
        
        # Handle student-specific fields if role is student
        if role == 'student':
            student_fields = {
                'student_id': validated_data.pop('student_id', None),
                'department': validated_data.pop('department', None),
                'year_of_study': validated_data.pop('year_of_study', None)
            }
            # Add student fields to validated_data
            validated_data.update(student_fields)
        
        # Create user
        user = User.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            **validated_data
        )
        
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data

    def validate_new_password(self, value):
        validate_password(value)
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type',
                 'department', 'phone_number', 'profile_picture', 'admin_category')
        read_only_fields = ('id', 'email', 'user_type')

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        try:
            validate_password(attrs['new_password'], self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    
    token = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs 