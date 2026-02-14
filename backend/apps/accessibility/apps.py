"""
App configuration for Accessibility
"""

from django.apps import AppConfig


class AccessibilityConfig(AppConfig):
    """Configuration for Accessibility app"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accessibility'
    verbose_name = 'Accessibility Features'
    
    def ready(self):
        """Initialize app signals and components"""
        # Import signals if any
        pass
