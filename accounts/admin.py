from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'user_type', 
                 'admin_category', 'student_id', 'department', 'year_of_study',
                 'is_staff', 'is_active')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admin_category'].required = False
        self.fields['student_id'].required = False
        self.fields['department'].required = False
        self.fields['year_of_study'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        admin_category = cleaned_data.get('admin_category')
        student_id = cleaned_data.get('student_id')
        department = cleaned_data.get('department')
        year_of_study = cleaned_data.get('year_of_study')
        
        if user_type == 'admin' and (not admin_category or admin_category == 'none'):
            self.add_error('admin_category', 'Admin category is required for admin accounts')
            
        if user_type == 'student':
            if not student_id:
                self.add_error('student_id', 'Student ID is required for student accounts')
            if not department:
                self.add_error('department', 'Department is required for student accounts')
            if not year_of_study:
                self.add_error('year_of_study', 'Year of study is required for student accounts')
            
        return cleaned_data

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('email', 'user_type', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'user_type', 'bio', 'profile_picture')}),
        ('Student info', {'fields': ('student_id', 'department', 'year_of_study'), 'classes': ('collapse',), 'description': 'Required for student accounts'}),
        ('Admin info', {'fields': ('admin_category',), 'classes': ('collapse',), 'description': 'Required for admin accounts'}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_staff_member', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type')}
        ),
        ('Student Info', {
            'classes': ('collapse',),
            'fields': ('student_id', 'department', 'year_of_study')}
        ),
        ('Admin Info', {
            'classes': ('collapse',),
            'fields': ('admin_category',)}
        ),
        ('Permissions', {
            'fields': ('is_staff', 'is_active')}
        ),
    )

    readonly_fields = ('last_login',)
    
    class Media:
        js = ('admin/js/admin_category.js',)
        
    def save_model(self, request, obj, form, change):
        """
        Set is_staff to True for admin users
        """
        if obj.user_type == 'admin':
            obj.is_staff = True
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)