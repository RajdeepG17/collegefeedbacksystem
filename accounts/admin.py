
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'admin_category', 'is_staff')
    list_filter = ('user_type', 'admin_category', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'profile_picture', 'phone_number', 'address')}),
        (_('User type'), {'fields': ('user_type', 'admin_category')}),
        (_('Student info'), {'fields': ('student_id', 'department', 'year_of_study')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type', 'admin_category'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name', 'student_id')
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at')