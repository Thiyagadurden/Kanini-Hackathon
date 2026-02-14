#!/usr/bin/env python
"""
Accessibility Features - Quick Setup Script
This script guides you through setting up the multilingual support system
"""

import os
import sys
import subprocess
import django

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(num, text):
    print(f"▶ Step {num}: {text}")

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n  → {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Success")
            return True
        else:
            print(f"  ✗ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def check_django_setup():
    """Check if Django is properly set up"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
        django.setup()
        return True
    except Exception as e:
        print(f"Django setup error: {e}")
        return False

def main():
    print_header("🌍 ACCESSIBILITY FEATURES - QUICK SETUP")
    
    print("""
This script will help you set up the multilingual translation and 
sign language support system for VoiceTriage.

The setup includes:
  ✓ Database migrations
  ✓ Django configuration
  ✓ Dependency installation
  ✓ Initial setup and testing

Let's get started!
    """)
    
    print_step(1, "Check Python and Django Setup")
    if not check_django_setup():
        print("  ✗ Django setup failed. Make sure you're in the backend directory.")
        return 1
    print("  ✓ Django is ready")
    
    print_step(2, "Check Django Settings")
    print("  Verifying accessibility app is in INSTALLED_APPS...")
    from django.conf import settings
    if 'apps.accessibility' in settings.INSTALLED_APPS:
        print("  ✓ Accessibility app is configured")
    else:
        print("  ✗ Add 'apps.accessibility' to INSTALLED_APPS in config/settings/base.py")
        return 1
    
    print_step(3, "Check URL Configuration")
    print("  Verifying accessibility URLs are included...")
    try:
        from django.urls import reverse
        reverse('language-preference-list')
        print("  ✓ Accessibility URLs are configured")
    except Exception as e:
        print(f"  ✗ URLs may not be configured correctly: {e}")
        print("  → Add to config/urls.py: path('api/accessibility/', include('apps.accessibility.urls'))")
    
    print_step(4, "Database Migrations")
    print("  Running database migrations...")
    
    if run_command(
        "python manage.py makemigrations apps.accessibility",
        "Creating migration files"
    ):
        print("  ✓ Migrations created")
    
    if run_command(
        "python manage.py migrate apps.accessibility",
        "Applying migrations to database"
    ):
        print("  ✓ Database tables created")
    else:
        print("  ✗ Migration failed")
        return 1
    
    print_step(5, "Install ML Dependencies")
    print("  Installing PyTorch and translation models (this may take a few minutes)...")
    
    # Check if torch is already installed
    try:
        import torch
        print(f"  ✓ PyTorch {torch.__version__} already installed")
    except ImportError:
        if run_command(
            "pip install torch --index-url https://download.pytorch.org/whl/cpu",
            "Installing PyTorch for CPU"
        ):
            print("  ✓ PyTorch installed")
        else:
            print("  ⚠ PyTorch installation failed")
            print("    → Install manually: pip install torch")
    
    # Check if transformers is installed
    try:
        import transformers
        print(f"  ✓ Transformers library already installed")
    except ImportError:
        if run_command(
            "pip install transformers",
            "Installing Hugging Face Transformers"
        ):
            print("  ✓ Transformers installed")
        else:
            print("  ⚠ Transformers installation failed")
            print("    → Install manually: pip install transformers")
    
    # Check if IndicTransToolkit is installed
    try:
        import IndicTransToolkit
        print(f"  ✓ IndicTransToolkit already installed")
    except ImportError:
        if run_command(
            "pip install IndicTransToolkit",
            "Installing IndicTransToolkit"
        ):
            print("  ✓ IndicTransToolkit installed")
        else:
            print("  ⚠ IndicTransToolkit installation failed (optional)")
    
    print_step(6, "Initial Setup")
    print("  Setting up language preferences for admin users...")
    
    if run_command(
        "python manage.py test_accessibility setup",
        "Running accessibility setup"
    ):
        print("  ✓ Setup complete")
    else:
        print("  ⚠ Setup command failed (non-critical)")
    
    print_step(7, "Verification")
    print("  Running validation checks...")
    
    if run_command(
        "python validate_accessibility.py",
        "Running validation script"
    ):
        print("  ✓ Validation passed")
    
    print_header("✅ SETUP COMPLETE")
    
    print("""
The accessibility features are now ready to use!

Next steps:

1. Start the development server:
   python manage.py runserver

2. Access the available endpoints:
   POST /api/accessibility/translation/translate/
   POST /api/accessibility/sign-language/convert_to_sign/
   GET  /api/accessibility/language-preference/
   
3. Test with curl:
   
   # Detect language
   curl -X POST http://localhost:8000/api/accessibility/language-preference/detect_language/ \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Hello"}'
   
   # Translate
   curl -X POST http://localhost:8000/api/accessibility/translation/translate/ \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{
       "text": "Hello world",
       "source_language": "english",
       "target_language": "hindi"
     }'
   
   # Convert to sign language
   curl -X POST http://localhost:8000/api/accessibility/sign-language/convert_to_sign/ \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{
       "text": "Thank you",
       "output_format": "animations"
     }'

4. Use in frontend:
   import MultilingualSupport from './components/Multilingual';
   import { useAccessibility } from './hooks/useAccessibility';
   import { TranslatableMessage } from './components/TranslationWidget';

5. Review integration examples:
   backend/ACCESSIBILITY_EXAMPLES.py

For more information and troubleshooting:
   - Check backend/ACCESSIBILITY_INTEGRATION.md (detailed guide)
   - Run: python manage.py test_accessibility test
   - View API docs: http://localhost:8000/api/accessibility/

Happy translating! 🌍
    """)
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
