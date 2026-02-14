"""
Views for Accessibility app
Handles multilingual translation and sign language support
"""

import hashlib
from datetime import datetime
from typing import Optional

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import (
    LanguagePreference,
    TranslatedContent,
    SignLanguageGlossary,
    AccessibilityLog,
)
from .serializers import (
    LanguagePreferenceSerializer,
    TranslatedContentSerializer,
    SignLanguageGlossarySerializer,
    AccessibilityLogSerializer,
    TranslationRequestSerializer,
    TranslationResponseSerializer,
    SignLanguageRequestSerializer,
    SignLanguageResponseSerializer,
)

# Import our custom services
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ai_engine', 'src'))

try:
    from translation_service import get_translator, get_language_names, detect_language
except ImportError:
    get_translator = None
    get_language_names = lambda: {}
    detect_language = lambda x: 'english'

try:
    from sign_language_support import get_sign_language_api
except ImportError:
    get_sign_language_api = None


class LanguagePreferenceViewSet(viewsets.ViewSet):
    """
    API endpoints for language preferences
    - Get/update user language preferences
    - List available languages
    - Auto-detect user language
    """
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all supported languages"""
        languages = get_language_names() if get_language_names else {
            'hindi': 'हिंदी (Hindi)',
            'english': 'English',
            'tamil': 'தமிழ் (Tamil)',
        }
        
        data = {
            'supported_languages': [
                {'code': code, 'name': name}
                for code, name in languages.items()
            ]
        }
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get current user's language preferences"""
        try:
            pref = LanguagePreference.objects.get(user=request.user)
            serializer = LanguagePreferenceSerializer(pref)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LanguagePreference.DoesNotExist:
            # Create default preferences
            pref = LanguagePreference.objects.create(user=request.user)
            serializer = LanguagePreferenceSerializer(pref)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def set_preferences(self, request):
        """Update user language preferences"""
        try:
            pref = LanguagePreference.objects.get(user=request.user)
        except LanguagePreference.DoesNotExist:
            pref = LanguagePreference.objects.create(user=request.user)
        
        serializer = LanguagePreferenceSerializer(pref, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def detect_language(self, request):
        """Auto-detect language of input text"""
        text = request.data.get('text', '')
        if not text:
            return Response(
                {'error': 'Text required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        detected = detect_language(text) if detect_language else 'english'
        
        return Response({
            'text': text,
            'detected_language': detected,
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)


class TranslationViewSet(viewsets.ViewSet):
    """
    API endpoints for multilingual translation
    - Translate text between languages
    - Cache translations
    - Batch translation
    """
    
    permission_classes = [IsAuthenticated]
    
    def _generate_content_hash(self, original_text: str, src_lang: str, tgt_lang: str) -> str:
        """Generate unique hash for translation request"""
        content = f"{original_text}_{src_lang}_{tgt_lang}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    @action(detail=False, methods=['post'])
    def translate(self, request):
        """
        Translate text from source to target language
        
        Request body:
        {
            "text": "Hello",
            "source_language": "english",
            "target_language": "hindi",
            "use_cache": true
        }
        """
        serializer = TranslationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text = serializer.validated_data['text']
        src_lang = serializer.validated_data['source_language']
        tgt_lang = serializer.validated_data['target_language']
        use_cache = serializer.validated_data['use_cache']
        
        # Check cache
        content_hash = self._generate_content_hash(text, src_lang, tgt_lang)
        cached = TranslatedContent.objects.filter(content_hash=content_hash).first()
        
        if cached and use_cache:
            cached.accessed_count += 1
            cached.save()
            
            response_data = {
                'original_text': cached.original_text,
                'source_language': cached.original_language,
                'translated_text': cached.translated_text,
                'target_language': cached.target_language,
                'from_cache': True,
                'timestamp': cached.last_accessed.isoformat(),
            }
            
            # Log usage
            AccessibilityLog.objects.create(
                user=request.user,
                feature='translation',
                source_language=src_lang,
                target_language=tgt_lang,
                details={'from_cache': True, 'text_length': len(text)}
            )
            
            response_serializer = TranslationResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        # Perform translation
        if not get_translator:
            return Response(
                {'error': 'Translation service not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        translator = get_translator()
        translated = translator.translate(text, src_lang, tgt_lang)
        
        if not translated:
            return Response(
                {'error': 'Translation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Cache the translation
        TranslatedContent.objects.update_or_create(
            content_hash=content_hash,
            defaults={
                'original_text': text,
                'original_language': src_lang,
                'translated_text': translated,
                'target_language': tgt_lang,
            }
        )
        
        response_data = {
            'original_text': text,
            'source_language': src_lang,
            'translated_text': translated,
            'target_language': tgt_lang,
            'from_cache': False,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Log usage
        AccessibilityLog.objects.create(
            user=request.user,
            feature='translation',
            source_language=src_lang,
            target_language=tgt_lang,
            details={'from_cache': False, 'text_length': len(text)}
        )
        
        response_serializer = TranslationResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def batch_translate(self, request):
        """
        Translate multiple texts at once
        
        Request body:
        {
            "texts": ["Hello", "Good morning"],
            "source_language": "english",
            "target_language": "hindi",
            "use_cache": true
        }
        """
        texts = request.data.get('texts', [])
        if not isinstance(texts, list):
            return Response(
                {'error': 'texts must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        src_lang = request.data.get('source_language')
        tgt_lang = request.data.get('target_language')
        
        if not all([texts, src_lang, tgt_lang]):
            return Response(
                {'error': 'texts, source_language, and target_language required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not get_translator:
            return Response(
                {'error': 'Translation service not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        translator = get_translator()
        translations = translator.batch_translate(texts, src_lang, tgt_lang)
        
        # Log usage
        AccessibilityLog.objects.create(
            user=request.user,
            feature='translation',
            source_language=src_lang,
            target_language=tgt_lang,
            details={'batch_size': len(texts)}
        )
        
        return Response({
            'original_texts': texts,
            'source_language': src_lang,
            'translated_texts': translations,
            'target_language': tgt_lang,
            'count': len(translations),
            'timestamp': datetime.now().isoformat(),
        }, status=status.HTTP_200_OK)


class SignLanguageViewSet(viewsets.ViewSet):
    """
    API endpoints for sign language support
    - Convert text to sign language
    - Get medical glossary
    - Get video references
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def convert_to_sign(self, request):
        """
        Convert text to sign language representation
        
        Request body:
        {
            "text": "Hello, how are you?",
            "output_format": "animations"  # animations|videos|hybrid
        }
        """
        serializer = SignLanguageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text = serializer.validated_data['text']
        output_format = serializer.validated_data['output_format']
        
        if not get_sign_language_api:
            return Response(
                {'error': 'Sign language service not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        api = get_sign_language_api()
        result = api.convert_to_sign(text, output_format)
        
        # Log usage
        AccessibilityLog.objects.create(
            user=request.user,
            feature='sign_language',
            details={'text_length': len(text), 'format': output_format}
        )
        
        response_serializer = SignLanguageResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def medical_glossary(self, request):
        """
        Get medical terms in sign language
        """
        if not get_sign_language_api:
            return Response(
                {'error': 'Sign language service not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        api = get_sign_language_api()
        glossary = api.get_medical_glossary()
        
        # Also get custom entries from database
        custom_entries = SignLanguageGlossary.objects.filter(is_medical=True)
        custom_serializer = SignLanguageGlossarySerializer(custom_entries, many=True)
        
        return Response({
            'built_in_glossary': glossary,
            'custom_entries': custom_serializer.data,
            'total_terms': len(glossary) + len(custom_entries),
        }, status=status.HTTP_200_OK)


class SignLanguageGlossaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for custom sign language glossary entries
    - CRUD operations on glossary entries
    - Filter by medical/non-medical terms
    - Search functionality
    """
    
    serializer_class = SignLanguageGlossarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter glossary entries"""
        queryset = SignLanguageGlossary.objects.all()
        
        # Filter by medical terms
        is_medical = self.request.query_params.get('is_medical')
        if is_medical:
            queryset = queryset.filter(is_medical=is_medical.lower() == 'true')
        
        # Search by word
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(word__icontains=search) | Q(meaning__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by when creating new glossary entry"""
        serializer.save(created_by=self.request.user)


class AccessibilityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for accessibility feature usage logging
    - Get usage statistics
    - Filter by feature type
    - Track user accessibility patterns
    """
    
    serializer_class = AccessibilityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get logs for current user"""
        queryset = AccessibilityLog.objects.filter(user=self.request.user)
        
        # Filter by feature
        feature = self.request.query_params.get('feature')
        if feature:
            queryset = queryset.filter(feature=feature)
        
        # Filter by language
        src_lang = self.request.query_params.get('source_language')
        if src_lang:
            queryset = queryset.filter(source_language=src_lang)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get accessibility usage statistics"""
        logs = AccessibilityLog.objects.filter(user=request.user)
        
        stats = {
            'total_features_used': logs.values('feature').distinct().count(),
            'feature_breakdown': {},
            'language_pairs': {},
            'total_requests': logs.count(),
        }
        
        # Feature usage
        for feature in ['translation', 'sign_language', 'text_to_speech', 'speech_to_text']:
            count = logs.filter(feature=feature).count()
            if count > 0:
                stats['feature_breakdown'][feature] = count
        
        # Language pairs
        translation_logs = logs.filter(feature='translation')
        for src_lang in translation_logs.values_list('source_language', flat=True).distinct():
            if src_lang:
                tgt_langs = translation_logs.filter(source_language=src_lang).values_list(
                    'target_language', flat=True
                ).distinct()
                stats['language_pairs'][src_lang] = list(tgt_langs)
        
        return Response(stats, status=status.HTTP_200_OK)
