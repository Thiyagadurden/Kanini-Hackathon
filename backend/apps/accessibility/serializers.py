"""
Serializers for Accessibility app
"""

from rest_framework import serializers
from .models import (
    LanguagePreference,
    TranslatedContent,
    SignLanguageGlossary,
    AccessibilityLog,
)


class LanguagePreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user language preferences"""
    
    class Meta:
        model = LanguagePreference
        fields = [
            'id',
            'user',
            'primary_language',
            'secondary_language',
            'translation_enabled',
            'sign_language_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TranslatedContentSerializer(serializers.ModelSerializer):
    """Serializer for cached translations"""
    
    class Meta:
        model = TranslatedContent
        fields = [
            'id',
            'original_text',
            'original_language',
            'translated_text',
            'target_language',
            'translation_model',
            'content_hash',
            'accessed_count',
            'created_at',
            'last_accessed',
        ]
        read_only_fields = [
            'id',
            'translated_text',
            'content_hash',
            'accessed_count',
            'created_at',
            'last_accessed',
        ]


class SignLanguageGlossarySerializer(serializers.ModelSerializer):
    """Serializer for sign language glossary"""
    
    created_by_email = serializers.CharField(
        source='created_by.email',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = SignLanguageGlossary
        fields = [
            'id',
            'word',
            'sign_name',
            'meaning',
            'hand_shape',
            'hand_position',
            'movement',
            'video_url',
            'description',
            'created_by',
            'created_by_email',
            'created_at',
            'updated_at',
            'is_medical',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccessibilityLogSerializer(serializers.ModelSerializer):
    """Serializer for accessibility usage logs"""
    
    user_email = serializers.CharField(
        source='user.email',
        read_only=True
    )
    
    class Meta:
        model = AccessibilityLog
        fields = [
            'id',
            'user',
            'user_email',
            'feature',
            'details',
            'source_language',
            'target_language',
            'timestamp',
        ]
        read_only_fields = [
            'id',
            'timestamp',
        ]


class TranslationRequestSerializer(serializers.Serializer):
    """Serializer for translation requests"""
    
    text = serializers.CharField(
        max_length=5000,
        help_text='Text to translate'
    )
    source_language = serializers.CharField(
        max_length=20,
        help_text='Source language code'
    )
    target_language = serializers.CharField(
        max_length=20,
        help_text='Target language code'
    )
    use_cache = serializers.BooleanField(
        default=True,
        help_text='Use cached translations if available'
    )


class TranslationResponseSerializer(serializers.Serializer):
    """Serializer for translation responses"""
    
    original_text = serializers.CharField()
    source_language = serializers.CharField()
    translated_text = serializers.CharField()
    target_language = serializers.CharField()
    from_cache = serializers.BooleanField()
    timestamp = serializers.DateTimeField()


class SignLanguageRequestSerializer(serializers.Serializer):
    """Serializer for sign language requests"""
    
    text = serializers.CharField(
        max_length=5000,
        help_text='Text to convert to sign language'
    )
    output_format = serializers.ChoiceField(
        choices=['animations', 'videos', 'hybrid'],
        default='animations',
        help_text='Output format for sign language'
    )


class SignGestureSerializer(serializers.Serializer):
    """Serializer for individual sign gestures"""
    
    sign = serializers.CharField()
    meaning = serializers.CharField()
    hand_shape = serializers.CharField()
    hand_position = serializers.CharField()
    movement = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    end_time = serializers.IntegerField()


class SignLanguageResponseSerializer(serializers.Serializer):
    """Serializer for sign language responses"""
    
    original_text = serializers.CharField()
    format = serializers.CharField()
    total_signs = serializers.IntegerField()
    total_duration_ms = serializers.IntegerField()
    animations = SignGestureSerializer(many=True, required=False)
    videos = serializers.ListField(child=serializers.DictField(), required=False)
    timestamp = serializers.DateTimeField()


class LanguageListSerializer(serializers.Serializer):
    """Serializer for language list"""
    
    code = serializers.CharField()
    name = serializers.CharField()
    native_name = serializers.CharField()
    script = serializers.CharField()


class MedicalGlossarySerializer(serializers.Serializer):
    """Serializer for medical glossary items"""
    
    word = serializers.CharField()
    sign_name = serializers.CharField()
    meaning = serializers.CharField()
    hand_shape = serializers.CharField()
    hand_position = serializers.CharField()
    movement = serializers.CharField()
    video_url = serializers.URLField(allow_null=True)
