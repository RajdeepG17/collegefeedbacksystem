
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profiles"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type', 'admin_category', 
                  'student_id', 'department', 'year_of_study', 'profile_picture', 
                  'phone_number', 'address', 'date_joined', 'full_name']
        read_only_fields = ['id', 'date_joined', 'full_name']

class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user information for public display"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'user_type']
        read_only_fields = fields
        
class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for listing admin users"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'admin_category']
        read_only_fields = fields

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'user_type',
                 'student_id', 'department', 'year_of_study']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
            
        # Student-specific validation
        if attrs.get('user_type') == 'student':
            if not attrs.get('student_id'):
                raise serializers.ValidationError({"student_id": "Student ID is required for student accounts."})
                
        return attrs
    
    def create(self, validated_data):
        # Remove password2 field
        validated_data.pop('password2', None)
        
        # Create user with encrypted password
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs