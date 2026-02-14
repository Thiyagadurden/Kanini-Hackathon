"""
Example integration of accessibility features into existing apps

This file shows how to integrate the translation and sign language
features into your chat, notification, and messaging systems.
"""

# ============================================================================
# EXAMPLE 1: Integrate translation into Chat Messages
# ============================================================================

# File: backend/apps/chat/views.py

from rest_framework import viewsets
from apps.accessibility.src.translation_service import get_translator
from apps.accessibility.models import AccessibilityLog
from rest_framework.decorators import action
from rest_framework.response import Response


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    Example of integrating translation into chat messages
    """

    @action(detail=False, methods=['post'])
    def translate_message(self, request):
        """
        Translate a chat message to the recipient's preferred language
        
        Usage:
            POST /api/chat/messages/translate_message/
            {
                "message_id": 123,
                "target_language": "hindi"
            }
        """
        message_id = request.data.get('message_id')
        target_language = request.data.get('target_language', 'english')
        
        try:
            # Get the message
            message = self.get_object()  # or Message.objects.get(id=message_id)
            original_text = message.content
            
            # Get translator
            translator = get_translator()
            
            # Translate
            translated_text = translator.translate(
                original_text,
                src_lang='english',
                tgt_lang=target_language
            )
            
            # Log the translation
            AccessibilityLog.objects.create(
                user=request.user,
                feature='translation',
                source_language='english',
                target_language=target_language,
                details={
                    'message_id': message_id,
                    'original_length': len(original_text),
                    'translated_length': len(translated_text)
                }
            )
            
            return Response({
                'original': original_text,
                'translated': translated_text,
                'language': target_language
            })
        except Exception as e:
            return Response({'error': str(e)}, status=503)


# ============================================================================
# EXAMPLE 2: Integrate translation into Notifications
# ============================================================================

# File: backend/apps/notifications/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from apps.accessibility.src.translation_service import get_translator
from apps.accessibility.models import LanguagePreference


@receiver(post_save, sender=Notification)
def translate_notification(sender, instance, created, **kwargs):
    """
    Signal handler to automatically translate notifications to user's language
    """
    if not created:
        return
    
    try:
        # Get user's language preference
        user_pref = LanguagePreference.objects.get(user=instance.user)
        
        if not user_pref.translation_enabled:
            return
        
        # Skip if already in user's language
        if user_pref.primary_language == 'english':
            return
        
        # Get translator
        translator = get_translator()
        
        # Translate title and message
        translated_title = translator.translate(
            instance.title,
            src_lang='english',
            tgt_lang=user_pref.primary_language
        )
        
        translated_message = translator.translate(
            instance.message,
            src_lang='english',
            tgt_lang=user_pref.primary_language
        )
        
        # Store translations (optional - update notification model if you add translation fields)
        # instance.translated_title = translated_title
        # instance.translated_message = translated_message
        # instance.save()
        
        print(f"Notification translated to {user_pref.primary_language}")
        
    except LanguagePreference.DoesNotExist:
        pass  # No preference set, skip translation
    except Exception as e:
        print(f"Error translating notification: {e}")


# ============================================================================
# EXAMPLE 3: Add translation to Prescription Instructions
# ============================================================================

# File: backend/apps/prescriptions/serializers.py

from rest_framework import serializers
from .models import Prescription
from apps.accessibility.src.translation_service import get_translator
from apps.accessibility.models import LanguagePreference


class AccessiblePrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer that includes translated prescription instructions
    """
    
    translated_instructions = serializers.SerializerMethodField()
    sign_language_instructions = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = ['id', 'medication', 'dosage', 'instructions', 
                  'translated_instructions', 'sign_language_instructions']
    
    def get_translated_instructions(self, obj):
        """Get prescription instructions in user's language"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return obj.instructions
        
        try:
            user_pref = LanguagePreference.objects.get(user=request.user)
            if not user_pref.translation_enabled or user_pref.primary_language == 'english':
                return obj.instructions
            
            translator = get_translator()
            translated = translator.translate(
                obj.instructions,
                src_lang='english',
                tgt_lang=user_pref.primary_language
            )
            return translated
        except Exception as e:
            print(f"Error translating instructions: {e}")
            return obj.instructions
    
    def get_sign_language_instructions(self, obj):
        """Get prescription instructions as sign language"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            user_pref = LanguagePreference.objects.get(user=request.user)
            if not user_pref.sign_language_enabled:
                return None
            
            from apps.accessibility.src.sign_language_support import get_sign_language_api
            api = get_sign_language_api()
            result = api.convert_to_sign(obj.instructions, 'animations')
            return result
        except Exception as e:
            print(f"Error converting to sign language: {e}")
            return None


# ============================================================================
# EXAMPLE 4: Batch translate patient messages
# ============================================================================

# File: backend/apps/patients/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.accessibility.src.translation_service import get_translator
from apps.accessibility.models import AccessibilityLog


class PatientViewSet(viewsets.ModelViewSet):
    """
    Example of batch translation for patient communications
    """
    
    @action(detail=True, methods=['post'])
    def translate_medical_records(self, request, pk=None):
        """
        Translate all medical records for a patient to a specific language
        
        Usage:
            POST /api/patients/{id}/translate_medical_records/
            {
                "target_language": "hindi"
            }
        """
        patient = self.get_object()
        target_language = request.data.get('target_language', 'english')
        
        try:
            # Collect all text to translate
            texts_to_translate = []
            
            # Add relevant medical information
            if patient.medical_history:
                texts_to_translate.append(patient.medical_history)
            
            if hasattr(patient, 'current_medications'):
                texts_to_translate.append(str(patient.current_medications))
            
            # Get translator
            translator = get_translator()
            
            # Batch translate
            if texts_to_translate:
                translated_texts = translator.batch_translate(
                    texts_to_translate,
                    src_lang='english',
                    tgt_lang=target_language
                )
            else:
                translated_texts = []
            
            # Log the batch translation
            AccessibilityLog.objects.create(
                user=request.user,
                feature='translation',
                source_language='english',
                target_language=target_language,
                details={
                    'patient_id': patient.id,
                    'texts_count': len(texts_to_translate),
                    'type': 'batch_medical_records'
                }
            )
            
            return Response({
                'original': texts_to_translate,
                'translated': translated_texts,
                'language': target_language,
                'count': len(translated_texts)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=503)


# ============================================================================
# EXAMPLE 5: Emergency alerts with sign language
# ============================================================================

# File: backend/apps/emergency/views.py

from apps.accessibility.src.sign_language_support import get_sign_language_api
from apps.accessibility.models import AccessibilityLog


def create_emergency_alert(patient, alert_message):
    """
    Create an emergency alert with sign language representation
    """
    try:
        # Get sign language API
        api = get_sign_language_api()
        
        # Convert alert message to sign language
        sign_sequence = api.convert_to_sign(
            alert_message,
            output_format='hybrid'  # Both animations and videos
        )
        
        # Store the alert (customize based on your model)
        alert_data = {
            'patient': patient,
            'message': alert_message,
            'sign_language': sign_sequence,  # Store gesture sequence
            'priority': 'critical'
        }
        
        # Log the emergency alert
        AccessibilityLog.objects.create(
            user=None,  # System alert, not user-specific
            feature='sign_language',
            source_language='english',
            details={
                'alert_type': 'emergency',
                'patient_id': patient.id,
                'sign_count': sign_sequence.get('total_signs', 0)
            }
        )
        
        return alert_data
    except Exception as e:
        print(f"Error creating emergency alert: {e}")
        return None


# ============================================================================
# EXAMPLE 6: Frontend - Use translation widget in existing components
# ============================================================================

# File: frontend/src/components/PatientChart.jsx

import React, { useState } from 'react';
import { TranslatableMessage, LanguageSelector } from './TranslationWidget';
import { useAccessibility } from '../hooks/useAccessibility';


export function PatientChart({ patient }) {
  const { preferences } = useAccessibility();
  const [selectedLanguage, setSelectedLanguage] = useState(preferences.primary_language);

  return (
    <div className="patient-chart">
      <div className="chart-header">
        <h2>{patient.name}</h2>
        {preferences.translation_enabled && (
          <div className="language-control">
            <label>View in:</label>
            <LanguageSelector
              value={selectedLanguage}
              onChange={setSelectedLanguage}
              size="small"
            />
          </div>
        )}
      </div>

      <div className="medical-history">
        <h3>Medical History</h3>
        <TranslatableMessage
          message={patient.medical_history}
          showOriginal={true}
        />
      </div>

      <div className="current-medications">
        <h3>Current Medications</h3>
        {patient.medications.map(med => (
          <TranslatableMessage
            key={med.id}
            message={`${med.name}: ${med.dosage}`}
          />
        ))}
      </div>

      <div className="instructions">
        <h3>Care Instructions</h3>
        <TranslatableMessage
          message={patient.care_instructions}
        />
      </div>
    </div>
  );
}


# ============================================================================
# EXAMPLE 7: Setup initialization in Django signals
# ============================================================================

# File: backend/config/apps.py

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'

    def ready(self):
        """Initialize accessibility features when app is ready"""
        from django.contrib.auth.models import User
        from apps.accessibility.models import LanguagePreference
        
        def initialize_accessibility(sender, **kwargs):
            """Ensure all users have language preferences"""
            for user in User.objects.filter(languagepreference__isnull=True):
                LanguagePreference.objects.create(
                    user=user,
                    primary_language='english'
                )
        
        post_migrate.connect(
            initialize_accessibility,
            sender=self,
            dispatch_uid='accessibility_init'
        )
