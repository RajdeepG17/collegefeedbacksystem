from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    FeedbackCategoryViewSet,
    FeedbackViewSet,
    FeedbackCommentViewSet
)

router = DefaultRouter()
router.register(r'categories', FeedbackCategoryViewSet)
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

feedback_router = routers.NestedSimpleRouter(router, r'feedbacks', lookup='feedback')
feedback_router.register(r'comments', FeedbackCommentViewSet, basename='feedback-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('feedback/<int:feedback_id>/', include(feedback_router.urls)),
]