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
        user = self.user
        data.update({
            'id': user.id,
            'email': user.email,
            'user_type': user.user_type,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'admin_category': user.admin_category if user.user_type == 'admin' else None,
        })
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'user_type', 
                 'admin_category', 'student_id', 'department', 'year_of_study', 'phone_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'user_type': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate user type specific fields
        user_type = attrs.get('user_type')
        if user_type == 'student':
            if not attrs.get('student_id'):
                raise serializers.ValidationError({"student_id": "Student ID is required for student accounts."})
            if not attrs.get('department'):
                raise serializers.ValidationError({"department": "Department is required for student accounts."})
            if not attrs.get('year_of_study'):
                raise serializers.ValidationError({"year_of_study": "Year of study is required for student accounts."})
        elif user_type == 'admin':
            if not attrs.get('admin_category') or attrs['admin_category'] == 'none':
                raise serializers.ValidationError({"admin_category": "Admin category is required for admin accounts."})
        
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'user_type', 'admin_category',
                 'student_id', 'department', 'year_of_study', 'profile_picture',
                 'phone_number', 'address', 'created_at', 'updated_at')
        read_only_fields = ('id', 'email', 'user_type', 'created_at', 'updated_at')

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