
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeedbackViewSet, FeedbackCategoryViewSet,
    FeedbackCommentViewSet, FeedbackHistoryViewSet,
)

router = DefaultRouter()
router.register(r'feedback', FeedbackViewSet)
router.register(r'categories', FeedbackCategoryViewSet)
router.register(r'comments', FeedbackCommentViewSet)
router.register(r'history', FeedbackHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]