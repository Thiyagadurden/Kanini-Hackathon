"""
Accessibility Setup Validator Script
Checks if all components are properly configured and ready to use
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.conf import settings
from django.db import connection
from django.apps import apps
import importlib


class AccessibilityValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []

    def check_all(self):
        """Run all validation checks"""
        print("\n" + "="*60)
        print("ACCESSIBILITY SETUP VALIDATOR")
        print("="*60 + "\n")

        self.check_installed_apps()
        self.check_database_tables()
        self.check_urls()
        self.check_dependencies()
        self.check_models()
        self.check_settings()

        self.print_results()

    def check_installed_apps(self):
        """Check if accessibility app is in INSTALLED_APPS"""
        print("1️⃣  Checking Django Apps...")

        if 'apps.accessibility' in settings.INSTALLED_APPS:
            self.success.append("✓ apps.accessibility is in INSTALLED_APPS")
        else:
            self.errors.append("✗ apps.accessibility NOT in INSTALLED_APPS")
            self.errors.append("  → Add 'apps.accessibility' to INSTALLED_APPS in settings/base.py")

    def check_database_tables(self):
        """Check if required database tables exist"""
        print("2️⃣  Checking Database Tables...")

        required_tables = [
            'accessibility_languagepreference',
            'accessibility_translatedcontent',
            'accessibility_signlanguageglossary',
            'accessibility_accessibilitylog'
        ]

        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}

        for table in required_tables:
            if table in existing_tables:
                self.success.append(f"✓ Table exists: {table}")
            else:
                self.errors.append(f"✗ Table missing: {table}")
                self.errors.append(
                    "  → Run: python manage.py migrate apps.accessibility"
                )

    def check_urls(self):
        """Check if accessibility URLs are configured"""
        print("3️⃣  Checking URL Configuration...")

        try:
            # Try to import and check the main URL config
            main_urls = importlib.import_module('config.urls')
            urlpatterns_str = str(main_urls.urlpatterns)

            if 'accessibility' in urlpatterns_str:
                self.success.append("✓ Accessibility URLs are configured")
            else:
                self.warnings.append("⚠ Accessibility URLs might not be included")
                self.warnings.append(
                    "  → Add to config/urls.py: "
                    "path('api/accessibility/', include('apps.accessibility.urls'))"
                )
        except Exception as e:
            self.warnings.append(f"⚠ Could not verify URLs: {str(e)}")

    def check_dependencies(self):
        """Check if required Python packages are installed"""
        print("4️⃣  Checking Python Dependencies...")

        required_packages = {
            'torch': 'PyTorch',
            'transformers': 'Hugging Face Transformers',
            'IndicTransToolkit': 'IndicTransToolkit',
        }

        optional_packages = {
            'numpy': 'NumPy (optional)',
            'pandas': 'Pandas (optional)',
        }

        # Check required
        for package, name in required_packages.items():
            try:
                importlib.import_module(package)
                self.success.append(f"✓ {name} is installed")
            except ImportError:
                self.errors.append(f"✗ {name} NOT installed")
                self.errors.append(f"  → Run: pip install {package}")

        # Check optional
        for package, name in optional_packages.items():
            try:
                importlib.import_module(package)
                self.success.append(f"✓ {name} is installed")
            except ImportError:
                self.warnings.append(f"⚠ {name} not installed (optional)")

    def check_models(self):
        """Check if all models are properly defined"""
        print("5️⃣  Checking Models...")

        try:
            from apps.accessibility.models import (
                LanguagePreference,
                TranslatedContent,
                SignLanguageGlossary,
                AccessibilityLog
            )

            self.success.append("✓ LanguagePreference model loaded")
            self.success.append("✓ TranslatedContent model loaded")
            self.success.append("✓ SignLanguageGlossary model loaded")
            self.success.append("✓ AccessibilityLog model loaded")

            # Check model counts
            counts = {
                'LanguagePreference': LanguagePreference.objects.count(),
                'TranslatedContent': TranslatedContent.objects.count(),
                'SignLanguageGlossary': SignLanguageGlossary.objects.count(),
                'AccessibilityLog': AccessibilityLog.objects.count(),
            }

            for model_name, count in counts.items():
                if count > 0:
                    self.success.append(f"  → {model_name}: {count} entries")

        except ImportError as e:
            self.errors.append(f"✗ Error importing models: {str(e)}")

    def check_settings(self):
        """Check relevant settings"""
        print("6️⃣  Checking Settings...")

        # Check CORS
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if cors_origins:
            self.success.append(f"✓ CORS configured with {len(cors_origins)} origins")
        else:
            self.warnings.append("⚠ CORS might need configuration for frontend access")

        # Check REST Framework
        if 'rest_framework' in settings.INSTALLED_APPS:
            self.success.append("✓ Django REST Framework is configured")
        else:
            self.errors.append("✗ Django REST Framework not found")

        # Check database
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite' in db_engine:
            self.success.append("✓ Using SQLite database")
        elif 'postgresql' in db_engine:
            self.success.append("✓ Using PostgreSQL database")
        else:
            self.success.append(f"✓ Using {db_engine} database")

    def print_results(self):
        """Print validation results"""
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60 + "\n")

        if self.success:
            print("✅ SUCCESS:")
            for msg in self.success:
                print(f"   {msg}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for msg in self.warnings:
                print(f"   {msg}")

        if self.errors:
            print("\n❌ ERRORS:")
            for msg in self.errors:
                print(f"   {msg}")

        print("\n" + "="*60)

        if self.errors:
            print("STATUS: ❌ CONFIGURATION INCOMPLETE")
            print("\nFix the errors above and run this script again.")
            return 1
        elif self.warnings:
            print("STATUS: ⚠️  CONFIGURATION WITH WARNINGS")
            print("\nThe system should work, but check the warnings above.")
            return 0
        else:
            print("STATUS: ✅ CONFIGURATION COMPLETE")
            print("\nAccessibility features are ready to use!")
            return 0

    def print_next_steps(self):
        """Print next steps"""
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60 + "\n")

        print("1. Start the development server:")
        print("   python manage.py runserver\n")

        print("2. Run the accessibility setup command:")
        print("   python manage.py test_accessibility setup\n")

        print("3. Test the features:")
        print("   python manage.py test_accessibility test\n")

        print("4. Access the admin panel:")
        print("   http://localhost:8000/admin/accessibility/\n")

        print("5. Try the API endpoints:")
        print("   http://localhost:8000/api/accessibility/language-preference/\n")

        print("6. Use the frontend components:")
        print("   import MultilingualSupport from './components/Multilingual'")
        print("   import { useAccessibility } from './hooks/useAccessibility'\n")


def main():
    """Run the validator"""
    validator = AccessibilityValidator()
    result = validator.check_all()

    if result == 0:
        validator.print_next_steps()

    return result


if __name__ == '__main__':
    sys.exit(main())
