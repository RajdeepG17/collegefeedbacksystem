"""
URL configuration for college_feedback_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from feedback.api_views import FeedbackViewSet, FeedbackResponseViewSet
from authentication.api_views import CreateUserView, LoginView, LogoutView

# Create a router for our API viewsets
router = DefaultRouter()
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')
router.register(r'responses', FeedbackResponseViewSet, basename='response')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/auth/register/', CreateUserView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='api-login'),
    path('api/auth/logout/', LogoutView.as_view(), name='api-logout'),
    
    # Include existing app URLs
    path('', include('feedback.urls')),
    path('accounts/', include('accounts.urls')),
    path('auth/', include('authentication.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
