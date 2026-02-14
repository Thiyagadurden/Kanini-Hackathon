from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NurseViewSet, NurseTaskViewSet

router = DefaultRouter()
router.register(r'', NurseViewSet, basename='nurse')
router.register(r'tasks', NurseTaskViewSet, basename='nurse-task')

urlpatterns = router.urls
