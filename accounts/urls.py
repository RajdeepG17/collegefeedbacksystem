
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserRegistrationView, LoginView, LogoutView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]