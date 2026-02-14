from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accessibility.models import (
    LanguagePreference,
    SignLanguageGlossary,
    AccessibilityLog
)


class Command(BaseCommand):
    help = 'Setup and test accessibility features'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['setup', 'test', 'populate', 'check'],
            help='Action to perform'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to test with'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'setup':
            self.setup_accessibility()
        elif action == 'test':
            self.test_translation()
        elif action == 'populate':
            self.populate_glossary()
        elif action == 'check':
            self.check_status()

    def setup_accessibility(self):
        """Initialize accessibility features"""
        self.stdout.write(self.style.SUCCESS('Setting up accessibility features...'))

        # Create language preferences for superusers
        for user in User.objects.filter(is_superuser=True):
            pref, created = LanguagePreference.objects.get_or_create(user=user)
            if created:
                pref.primary_language = 'english'
                pref.secondary_language = 'hindi'
                pref.translation_enabled = True
                pref.sign_language_enabled = True
                pref.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created preferences for {user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Preferences already exist for {user.username}')
                )

        self.stdout.write(self.style.SUCCESS('Accessibility setup complete!'))

    def test_translation(self):
        """Test translation service"""
        self.stdout.write(self.style.SUCCESS('Testing translation service...'))

        try:
            from apps.accessibility.src.translation_service import (
                get_translator,
                detect_language
            )

            self.stdout.write('→ Loading translation model (first time may take a while)...')
            translator = get_translator()
            self.stdout.write(self.style.SUCCESS('✓ Model loaded successfully'))

            # Test language detection
            test_texts = [
                ('Hello', 'english'),
                ('नमस्ते', 'hindi'),
                ('வணக்கம்', 'tamil'),
            ]

            self.stdout.write('\n→ Testing language detection:')
            for text, expected in test_texts:
                detected = detect_language(text)
                status = '✓' if detected == expected else '✗'
                self.stdout.write(f'  {status} {text} → {detected} (expected {expected})')

            # Test translation
            self.stdout.write('\n→ Testing translation:')
            result = translator.translate('Hello', 'english', 'hindi')
            self.stdout.write(f'  ✓ "Hello" → "{result}"')

            self.stdout.write(self.style.SUCCESS('\nTranslation test passed!'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Translation test failed: {str(e)}')
            )

    def test_sign_language(self):
        """Test sign language service"""
        self.stdout.write(self.style.SUCCESS('Testing sign language service...'))

        try:
            from apps.accessibility.src.sign_language_support import (
                get_sign_language_api
            )

            api = get_sign_language_api()
            self.stdout.write('✓ Sign language API initialized')

            # Test conversion
            result = api.convert_to_sign('Hello', 'animations')
            self.stdout.write(
                f'✓ "Hello" → {result["total_signs"]} signs, '
                f'{result["total_duration_ms"]}ms duration'
            )

            # Test medical glossary
            medical = api.get_medical_glossary()
            self.stdout.write(f'✓ Medical glossary loaded: {len(medical)} entries')

            self.stdout.write(self.style.SUCCESS('Sign language test passed!'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Sign language test failed: {str(e)}')
            )

    def populate_glossary(self):
        """Populate custom sign glossary"""
        self.stdout.write(self.style.SUCCESS('Populating sign language glossary...'))

        medical_signs = [
            {
                'word': 'blood_pressure',
                'sign_name': 'blood_pressure_sign',
                'meaning': 'Blood pressure measurement',
                'hand_shape': 'open_hand',
                'hand_position': 'arm',
                'movement': 'squeeze',
                'video_url': 'https://example.com/blood_pressure.mp4',
                'description': 'Squeeze arm to indicate blood pressure measurement',
                'is_medical': True
            },
            {
                'word': 'temperature',
                'sign_name': 'temperature_sign',
                'meaning': 'Temperature check',
                'hand_shape': 'pinch_hand',
                'hand_position': 'mouth',
                'movement': 'stab',
                'video_url': 'https://example.com/temperature.mp4',
                'description': 'Place thermometer in mouth',
                'is_medical': True
            },
            {
                'word': 'surgery',
                'sign_name': 'surgery_sign',
                'meaning': 'Surgical operation',
                'hand_shape': 'open_hand',
                'hand_position': 'chest',
                'movement': 'cutting',
                'video_url': 'https://example.com/surgery.mp4',
                'description': 'Cutting motion indicating surgery',
                'is_medical': True
            }
        ]

        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('✗ No admin user found'))
            return

        count = 0
        for sign_data in medical_signs:
            obj, created = SignLanguageGlossary.objects.get_or_create(
                word=sign_data['word'],
                defaults={**sign_data, 'created_by': admin_user}
            )
            if created:
                count += 1
                self.stdout.write(f'✓ Added {sign_data["word"]}')
            else:
                self.stdout.write(f'→ {sign_data["word"]} already exists')

        self.stdout.write(
            self.style.SUCCESS(f'\nGlossary updated: {count} new entries added')
        )

    def check_status(self):
        """Check accessibility system status"""
        self.stdout.write(self.style.SUCCESS('Checking accessibility status...\n'))

        # Check models
        self.stdout.write('Database Models:')
        prefs_count = LanguagePreference.objects.count()
        glossary_count = SignLanguageGlossary.objects.count()
        logs_count = AccessibilityLog.objects.count()

        self.stdout.write(f'  ✓ LanguagePreference: {prefs_count} entries')
        self.stdout.write(f'  ✓ SignLanguageGlossary: {glossary_count} entries')
        self.stdout.write(f'  ✓ AccessibilityLog: {logs_count} entries')

        # Check settings
        self.stdout.write('\nDjango Settings:')
        from django.conf import settings
        has_app = 'apps.accessibility' in settings.INSTALLED_APPS
        self.stdout.write(f'  {"✓" if has_app else "✗"} App in INSTALLED_APPS')

        # Check API
        self.stdout.write('\nAPI Endpoints:')
        from django.urls import reverse, NoReverseMatch
        endpoints = [
            'language-preference-list',
            'translation-list',
            'sign-language-list',
        ]

        for endpoint in endpoints:
            try:
                url = reverse(endpoint)
                self.stdout.write(f'  ✓ {endpoint}')
            except NoReverseMatch:
                self.stdout.write(f'  ✗ {endpoint} not found')

        self.stdout.write(self.style.SUCCESS('\nStatus check complete!'))
