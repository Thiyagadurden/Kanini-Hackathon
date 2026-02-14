"""
Accessibility App Models for multilingual and sign language support
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LanguagePreference(models.Model):
    """User language preferences"""
    
    LANGUAGE_CHOICES = [
        ('hindi', 'हिंदी (Hindi)'),
        ('tamil', 'தமிழ் (Tamil)'),
        ('telugu', 'తెలుగు (Telugu)'),
        ('kannada', 'ಕನ್ನಡ (Kannada)'),
        ('malayalam', 'മലയാളം (Malayalam)'),
        ('marathi', 'मराठी (Marathi)'),
        ('gujarati', 'ગુજરાતી (Gujarati)'),
        ('bengali', 'বাংলা (Bengali)'),
        ('punjabi', 'ਪੰਜਾਬੀ (Punjabi)'),
        ('urdu', 'اردو (Urdu)'),
        ('english', 'English'),
        ('odia', 'ଓଡ଼ିଆ (Odia)'),
        ('assamese', 'অসমীয়া (Assamese)'),
        ('kashmiri', 'کاشُر (Kashmiri)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='language_preference')
    primary_language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='english',
        help_text='Primary language for user interface'
    )
    secondary_language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='english',
        help_text='Secondary language for communication'
    )
    translation_enabled = models.BooleanField(
        default=True,
        help_text='Enable automatic translation'
    )
    sign_language_enabled = models.BooleanField(
        default=False,
        help_text='Enable sign language support'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Language Preference'
        verbose_name_plural = 'Language Preferences'
    
    def __str__(self):
        return f"{self.user.email} - {self.primary_language}"


class TranslatedContent(models.Model):
    """Cache translated content to reduce API calls"""
    
    original_text = models.TextField(
        help_text='Original text before translation'
    )
    original_language = models.CharField(
        max_length=20,
        help_text='Original language code'
    )
    translated_text = models.TextField(
        help_text='Translated text'
    )
    target_language = models.CharField(
        max_length=20,
        help_text='Target language code'
    )
    translation_model = models.CharField(
        max_length=100,
        default='indictrans2-indic-en-1B',
        help_text='Model used for translation'
    )
    content_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text='Hash of original_text + original_language + target_language'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accessed_count = models.IntegerField(default=1, help_text='Times this translation was accessed')
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Translated Content'
        verbose_name_plural = 'Translated Content'
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['original_language', 'target_language']),
        ]
    
    def __str__(self):
        return f"{self.original_language} -> {self.target_language}: {self.original_text[:50]}"


class SignLanguageGlossary(models.Model):
    """Custom sign language glossary entries"""
    
    word = models.CharField(
        max_length=100,
        unique=True,
        help_text='Word to translate to sign'
    )
    sign_name = models.CharField(
        max_length=100,
        help_text='Name of the sign gesture'
    )
    meaning = models.TextField(
        help_text='What the sign means'
    )
    hand_shape = models.CharField(
        max_length=50,
        help_text='Hand configuration'
    )
    hand_position = models.CharField(
        max_length=50,
        help_text='Position relative to body'
    )
    movement = models.CharField(
        max_length=100,
        help_text='Type of movement'
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text='URL to sign language video'
    )
    description = models.TextField(
        blank=True,
        help_text='Detailed description of the sign'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='User who created this entry'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_medical = models.BooleanField(
        default=False,
        help_text='Medical terminology'
    )
    
    class Meta:
        verbose_name = 'Sign Language Glossary'
        verbose_name_plural = 'Sign Language Glossaries'
        indexes = [
            models.Index(fields=['word']),
            models.Index(fields=['is_medical']),
        ]
    
    def __str__(self):
        return f"{self.word}: {self.sign_name}"


class AccessibilityLog(models.Model):
    """Log accessibility feature usage"""
    
    FEATURE_CHOICES = [
        ('translation', 'Translation'),
        ('sign_language', 'Sign Language'),
        ('text_to_speech', 'Text to Speech'),
        ('speech_to_text', 'Speech to Text'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='accessibility_logs'
    )
    feature = models.CharField(
        max_length=20,
        choices=FEATURE_CHOICES
    )
    details = models.JSONField(
        default=dict,
        help_text='Feature-specific details'
    )
    source_language = models.CharField(
        max_length=20,
        blank=True,
        help_text='Source language for translation'
    )
    target_language = models.CharField(
        max_length=20,
        blank=True,
        help_text='Target language for translation'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Accessibility Log'
        verbose_name_plural = 'Accessibility Logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['feature']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.feature} at {self.timestamp}"
