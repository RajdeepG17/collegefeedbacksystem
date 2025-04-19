from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeedbackCategoryViewSet, FeedbackViewSet,
    FeedbackCommentViewSet, FeedbackHistoryViewSet
)

router = DefaultRouter()
router.register(r'categories', FeedbackCategoryViewSet, basename='category')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

# Nested routers for comments and history
feedback_router = DefaultRouter()
feedback_router.register(r'comments', FeedbackCommentViewSet, basename='feedback-comment')
feedback_router.register(r'history', FeedbackHistoryViewSet, basename='feedback-history')

urlpatterns = [
    path('', include(router.urls)),
    path('feedback/<int:feedback_id>/', include(feedback_router.urls)),
]