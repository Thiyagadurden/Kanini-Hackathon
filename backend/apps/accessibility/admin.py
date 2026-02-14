"""
Admin configuration for Accessibility app
"""

from django.contrib import admin
from .models import (
    LanguagePreference,
    TranslatedContent,
    SignLanguageGlossary,
    AccessibilityLog,
)


@admin.register(LanguagePreference)
class LanguagePreferenceAdmin(admin.ModelAdmin):
    """Admin interface for language preferences"""
    
    list_display = [
        'user',
        'primary_language',
        'secondary_language',
        'translation_enabled',
        'sign_language_enabled',
        'updated_at',
    ]
    list_filter = [
        'primary_language',
        'translation_enabled',
        'sign_language_enabled',
        'updated_at',
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Language Settings', {
            'fields': (
                'primary_language',
                'secondary_language',
            )
        }),
        ('Feature Settings', {
            'fields': (
                'translation_enabled',
                'sign_language_enabled',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TranslatedContent)
class TranslatedContentAdmin(admin.ModelAdmin):
    """Admin interface for translation cache"""
    
    list_display = [
        'original_language',
        'target_language',
        'original_text',
        'accessed_count',
        'created_at',
    ]
    list_filter = [
        'original_language',
        'target_language',
        'translation_model',
        'created_at',
    ]
    search_fields = ['original_text', 'translated_text']
    readonly_fields = [
        'content_hash',
        'created_at',
        'last_accessed',
        'accessed_count',
    ]
    
    def original_text(self, obj):
        """Truncate original text for display"""
        return obj.original_text[:100] + '...' if len(obj.original_text) > 100 else obj.original_text
    original_text.short_description = 'Original Text'


@admin.register(SignLanguageGlossary)
class SignLanguageGlossaryAdmin(admin.ModelAdmin):
    """Admin interface for sign language glossary"""
    
    list_display = [
        'word',
        'sign_name',
        'is_medical',
        'hand_shape',
        'hand_position',
        'movement',
        'created_by',
        'created_at',
    ]
    list_filter = [
        'is_medical',
        'hand_shape',
        'hand_position',
        'created_at',
    ]
    search_fields = ['word', 'sign_name', 'meaning']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Sign Information', {
            'fields': (
                'word',
                'sign_name',
                'meaning',
            )
        }),
        ('Hand Configuration', {
            'fields': (
                'hand_shape',
                'hand_position',
                'movement',
            )
        }),
        ('Media', {
            'fields': ('video_url',)
        }),
        ('Classification', {
            'fields': ('is_medical',)
        }),
        ('Additional Information', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AccessibilityLog)
class AccessibilityLogAdmin(admin.ModelAdmin):
    """Admin interface for accessibility logs"""
    
    list_display = [
        'user',
        'feature',
        'source_language',
        'target_language',
        'timestamp',
    ]
    list_filter = [
        'feature',
        'source_language',
        'target_language',
        'timestamp',
    ]
    search_fields = ['user__email', 'feature']
    readonly_fields = ['timestamp', 'details']
    
    def has_add_permission(self, request):
        """Prevent manual creation of logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of logs"""
        return False
