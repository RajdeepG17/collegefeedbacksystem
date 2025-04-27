from django.urls import path
# Minimal views for the frontend demo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from . import views

# Simple login view function
@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        # Return a simple login page for GET requests
        return render(request, 'login.html', {})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # For demo purposes, check against hardcoded credentials
            if email == 'student@example.com' and password == 'studentpass':
                return JsonResponse({
                    'status': 'success',
                    'user': {
                        'id': 1,
                        'email': email,
                        'role': 'student'
                    }
                })
            elif email == 'admin@example.com' and password == 'adminpass':
                return JsonResponse({
                    'status': 'success',
                    'user': {
                        'id': 2,
                        'email': email,
                        'role': 'admin'
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid credentials'
                }, status=401)
        except:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

# Simple logout view function
@csrf_exempt
def logout_view(request):
    if request.method == 'GET':
        # Handle GET requests to logout endpoint
        return JsonResponse({
            'status': 'error',
            'message': 'Please use POST method to logout'
        })
    
    elif request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': 'Logged out successfully'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

# URL patterns
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
] 