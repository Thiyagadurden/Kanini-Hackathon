"""
URLs for Accessibility app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'language-preference', views.LanguagePreferenceViewSet, basename='language-preference')
router.register(r'translation', views.TranslationViewSet, basename='translation')
router.register(r'sign-language', views.SignLanguageViewSet, basename='sign-language')
router.register(r'glossary', views.SignLanguageGlossaryViewSet, basename='glossary')
router.register(r'logs', views.AccessibilityLogViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]
