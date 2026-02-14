# Generated migration for accessibility app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguagePreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_language', models.CharField(
                    choices=[
                        ('hindi', 'Hindi'),
                        ('english', 'English'),
                        ('tamil', 'Tamil'),
                        ('telugu', 'Telugu'),
                        ('kannada', 'Kannada'),
                        ('malayalam', 'Malayalam'),
                        ('marathi', 'Marathi'),
                        ('gujarati', 'Gujarati'),
                        ('bengali', 'Bengali'),
                        ('punjabi', 'Punjabi'),
                        ('urdu', 'Urdu'),
                        ('odia', 'Odia'),
                        ('assamese', 'Assamese'),
                        ('kashmiri', 'Kashmiri'),
                    ],
                    default='english',
                    max_length=20
                )),
                ('secondary_language', models.CharField(
                    choices=[
                        ('hindi', 'Hindi'),
                        ('english', 'English'),
                        ('tamil', 'Tamil'),
                        ('telugu', 'Telugu'),
                        ('kannada', 'Kannada'),
                        ('malayalam', 'Malayalam'),
                        ('marathi', 'Marathi'),
                        ('gujarati', 'Gujarati'),
                        ('bengali', 'Bengali'),
                        ('punjabi', 'Punjabi'),
                        ('urdu', 'Urdu'),
                        ('odia', 'Odia'),
                        ('assamese', 'Assamese'),
                        ('kashmiri', 'Kashmiri'),
                    ],
                    default='english',
                    max_length=20
                )),
                ('translation_enabled', models.BooleanField(default=False)),
                ('sign_language_enabled', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Language Preference', 'verbose_name_plural': 'Language Preferences'},
        ),
        migrations.CreateModel(
            name='TranslatedContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_text', models.TextField()),
                ('original_language', models.CharField(max_length=20)),
                ('translated_text', models.TextField()),
                ('target_language', models.CharField(max_length=20)),
                ('content_hash', models.CharField(max_length=64, unique=True, db_index=True)),
                ('accessed_count', models.IntegerField(default=0)),
                ('last_accessed', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Translated Content', 'verbose_name_plural': 'Translated Contents', 'indexes': [models.Index(fields=['content_hash'], name='content_hash_idx')]},
        ),
        migrations.CreateModel(
            name='SignLanguageGlossary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100)),
                ('sign_name', models.CharField(max_length=100)),
                ('meaning', models.TextField()),
                ('hand_shape', models.CharField(max_length=50)),
                ('hand_position', models.CharField(max_length=50)),
                ('movement', models.CharField(max_length=50)),
                ('video_url', models.URLField(blank=True, null=True)),
                ('description', models.TextField()),
                ('is_medical', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Sign Language Glossary Entry', 'verbose_name_plural': 'Sign Language Glossary'},
        ),
        migrations.CreateModel(
            name='AccessibilityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature', models.CharField(
                    choices=[
                        ('translation', 'Translation'),
                        ('sign_language', 'Sign Language'),
                        ('text_to_speech', 'Text to Speech'),
                        ('speech_to_text', 'Speech to Text'),
                    ],
                    max_length=20
                )),
                ('source_language', models.CharField(blank=True, max_length=20, null=True)),
                ('target_language', models.CharField(blank=True, max_length=20, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('details', models.JSONField(default=dict)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Accessibility Log', 'verbose_name_plural': 'Accessibility Logs', 'indexes': [models.Index(fields=['user', 'feature'], name='user_feature_idx'), models.Index(fields=['content_hash'], name='content_hash_idx')]},
        ),
    ]
