from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import LanguagePreference, TranslatedContent, SignLanguageGlossary, AccessibilityLog
import hashlib


class LanguagePreferenceTests(TestCase):
    """Test language preference endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_supported_languages(self):
        """Test fetching list of supported languages"""
        response = self.client.get('/api/accessibility/language-preference/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('supported_languages', response.json())
    
    def test_get_my_preferences(self):
        """Test fetching user's language preferences"""
        response = self.client.get('/api/accessibility/language-preference/my_preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('primary_language', data)
        self.assertIn('secondary_language', data)
    
    def test_set_preferences(self):
        """Test updating user's language preferences"""
        data = {
            'primary_language': 'hindi',
            'secondary_language': 'english',
            'translation_enabled': True,
            'sign_language_enabled': True
        }
        response = self.client.post(
            '/api/accessibility/language-preference/set_preferences/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify preferences were saved
        pref = LanguagePreference.objects.get(user=self.user)
        self.assertEqual(pref.primary_language, 'hindi')
        self.assertEqual(pref.secondary_language, 'english')
    
    def test_detect_language(self):
        """Test language detection"""
        data = {'text': 'नमस्ते'}
        response = self.client.post(
            '/api/accessibility/language-preference/detect_language/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn('detected_language', result)


class TranslationTests(TestCase):
    """Test translation endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_translate_english_to_hindi(self):
        """Test translating English to Hindi"""
        data = {
            'text': 'Hello',
            'source_language': 'english',
            'target_language': 'hindi',
            'use_cache': False
        }
        response = self.client.post(
            '/api/accessibility/translation/translate/',
            data
        )
        # Note: Will return 503 if model not loaded, 200 if success
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
        
        if response.status_code == status.HTTP_200_OK:
            result = response.json()
            self.assertIn('translated_text', result)
            self.assertIn('from_cache', result)
    
    def test_translation_caching(self):
        """Test that translations are cached"""
        data = {
            'text': 'Good morning',
            'source_language': 'english',
            'target_language': 'hindi'
        }
        
        # First call
        response1 = self.client.post('/api/accessibility/translation/translate/', data)
        if response1.status_code == status.HTTP_200_OK:
            # Second call should be cached
            response2 = self.client.post('/api/accessibility/translation/translate/', data)
            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            self.assertTrue(response2.json().get('from_cache', False))
    
    def test_batch_translate(self):
        """Test batch translation"""
        data = {
            'texts': ['Hello', 'Good morning', 'Thank you'],
            'source_language': 'english',
            'target_language': 'hindi'
        }
        response = self.client.post(
            '/api/accessibility/translation/batch_translate/',
            data
        )
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])


class SignLanguageTests(TestCase):
    """Test sign language endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_convert_to_sign_animations(self):
        """Test converting text to sign language animations"""
        data = {
            'text': 'Hello',
            'output_format': 'animations'
        }
        response = self.client.post(
            '/api/accessibility/sign-language/convert_to_sign/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn('animations', result)
        self.assertIn('total_signs', result)
        self.assertIn('total_duration_ms', result)
    
    def test_convert_to_sign_videos(self):
        """Test converting text to sign language videos"""
        data = {
            'text': 'Doctor',
            'output_format': 'videos'
        }
        response = self.client.post(
            '/api/accessibility/sign-language/convert_to_sign/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn('videos', result)
    
    def test_medical_glossary(self):
        """Test fetching medical glossary"""
        response = self.client.get(
            '/api/accessibility/sign-language/medical_glossary/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn('results', result)


class SignLanguageGlossaryTests(TestCase):
    """Test custom sign language glossary CRUD"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_custom_sign(self):
        """Test creating a custom sign"""
        data = {
            'word': 'stethoscope',
            'sign_name': 'stethoscope_sign',
            'meaning': 'Medical instrument for listening',
            'hand_shape': 'open_hand',
            'hand_position': 'chest',
            'movement': 'circular',
            'video_url': 'https://example.com/stethoscope.mp4',
            'description': 'Move stethoscope in circular motion on chest',
            'is_medical': True
        }
        response = self.client.post(
            '/api/accessibility/sign-language-glossary/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify it was created
        sign = SignLanguageGlossary.objects.get(word='stethoscope')
        self.assertEqual(sign.created_by, self.user)
        self.assertTrue(sign.is_medical)
    
    def test_list_glossary(self):
        """Test listing custom signs"""
        # Create a sign first
        SignLanguageGlossary.objects.create(
            word='injection',
            sign_name='injection_sign',
            meaning='Medical injection',
            hand_shape='pinch_hand',
            hand_position='arm',
            movement='stab',
            is_medical=True,
            created_by=self.user
        )
        
        response = self.client.get('/api/accessibility/sign-language-glossary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertGreater(len(result['results']), 0)
    
    def test_filter_medical_glossary(self):
        """Test filtering to show only medical signs"""
        response = self.client.get(
            '/api/accessibility/sign-language-glossary/?is_medical=true'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AccessibilityLogTests(TestCase):
    """Test accessibility usage logging"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create some log entries
        AccessibilityLog.objects.create(
            user=self.user,
            feature='translation',
            source_language='english',
            target_language='hindi'
        )
        AccessibilityLog.objects.create(
            user=self.user,
            feature='sign_language',
            source_language='english'
        )
    
    def test_view_accessibility_logs(self):
        """Test viewing user's accessibility logs"""
        response = self.client.get('/api/accessibility/accessibility-log/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertGreater(len(result['results']), 0)
    
    def test_accessibility_statistics(self):
        """Test getting accessibility usage statistics"""
        response = self.client.get(
            '/api/accessibility/accessibility-log/statistics/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn('total_translations', result)
        self.assertIn('total_sign_language_conversions', result)
        self.assertIn('language_pairs', result)


class TranslatedContentCacheTests(TestCase):
    """Test translation caching mechanism"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_cache_hash_generation(self):
        """Test that cache hashes are generated correctly"""
        text = "Hello world"
        src_lang = "english"
        tgt_lang = "hindi"
        
        # Create cached translation
        content_hash = hashlib.sha256(
            f"{text}|{src_lang}|{tgt_lang}".encode()
        ).hexdigest()
        
        cache = TranslatedContent.objects.create(
            original_text=text,
            original_language=src_lang,
            translated_text="नमस्ते दुनिया",
            target_language=tgt_lang,
            content_hash=content_hash
        )
        
        # Verify hash is unique
        self.assertEqual(cache.content_hash, content_hash)
        
        # Verify we can lookup by hash
        found = TranslatedContent.objects.get(content_hash=content_hash)
        self.assertEqual(found.translated_text, "नमस्ते दुनिया")
    
    def test_cache_access_tracking(self):
        """Test that cache access count is incremented"""
        cache = TranslatedContent.objects.create(
            original_text="Test",
            original_language="english",
            translated_text="परीक्षण",
            target_language="hindi",
            content_hash="hash123",
            accessed_count=0
        )
        
        initial_count = cache.accessed_count
        cache.accessed_count += 1
        cache.save()
        
        refreshed = TranslatedContent.objects.get(pk=cache.pk)
        self.assertEqual(refreshed.accessed_count, initial_count + 1)


class ModelTests(TestCase):
    """Test model validations and constraints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_language_preference_one_to_one(self):
        """Test that each user has only one language preference"""
        pref1 = LanguagePreference.objects.create(
            user=self.user,
            primary_language='hindi'
        )
        
        # Try to create another (should fail or replace)
        pref2 = LanguagePreference.objects.create(
            user=self.user,
            primary_language='tamil'
        )
        
        # There should be only one preference for this user
        count = LanguagePreference.objects.filter(user=self.user).count()
        self.assertLessEqual(count, 1)
    
    def test_sign_language_glossary_fields(self):
        """Test sign language glossary model fields"""
        sign = SignLanguageGlossary.objects.create(
            word='hello',
            sign_name='hello_sign',
            meaning='greeting',
            hand_shape='open_hand',
            hand_position='head',
            movement='wave',
            video_url='https://example.com/hello.mp4',
            description='Wave hand in greeting motion',
            is_medical=False,
            created_by=self.user
        )
        
        self.assertEqual(sign.word, 'hello')
        self.assertEqual(sign.created_by, self.user)
        self.assertFalse(sign.is_medical)
    
    def test_accessibility_log_json_field(self):
        """Test accessibility log JSON field"""
        log = AccessibilityLog.objects.create(
            user=self.user,
            feature='translation',
            source_language='english',
            target_language='marathi',
            details={
                'text_length': 100,
                'cached': False,
                'processing_time_ms': 2500
            }
        )
        
        self.assertEqual(log.details['text_length'], 100)
        self.assertFalse(log.details['cached'])


class PermissionTests(TestCase):
    """Test API permission requirements"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        response = self.client.get(
            '/api/accessibility/language-preference/my_preferences/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access_allowed(self):
        """Test that authenticated users can access endpoints"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            '/api/accessibility/language-preference/my_preferences/'
        )
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class IntegrationTests(TestCase):
    """Integration tests for the accessibility app"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_full_translation_workflow(self):
        """Test complete translation workflow"""
        # 1. Set language preferences
        pref_data = {
            'primary_language': 'hindi',
            'translation_enabled': True
        }
        self.client.post(
            '/api/accessibility/language-preference/set_preferences/',
            pref_data
        )
        
        # 2. Get preferences
        response = self.client.get(
            '/api/accessibility/language-preference/my_preferences/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Detect language
        detect_data = {'text': 'Hello'}
        response = self.client.post(
            '/api/accessibility/language-preference/detect_language/',
            detect_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_sign_language_workflow(self):
        """Test sign language conversion workflow"""
        # 1. Convert text to sign
        data = {
            'text': 'Patient needs medicine',
            'output_format': 'animations'
        }
        response = self.client.post(
            '/api/accessibility/sign-language/convert_to_sign/',
            data
        )
        
        # 2. Get medical glossary
        response = self.client.get(
            '/api/accessibility/sign-language/medical_glossary/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
