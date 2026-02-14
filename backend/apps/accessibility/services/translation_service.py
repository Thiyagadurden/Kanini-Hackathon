"""
IndicTrans2-based Translation Service
Handles multilingual translation for Indian languages
Supports: English, Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Bengali, Punjabi, Urdu, Odia, Assamese
"""

import logging

logger = logging.getLogger(__name__)


class MultilingualTranslator:
    """
    Multilingual translation using IndicTrans2
    Focuses on Indian languages with high quality translation
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'bn': 'Bengali',
        'pa': 'Punjabi',
        'ur': 'Urdu',
        'or': 'Odia',
        'as': 'Assamese'
    }
    
    # Language code mappings for IndicTrans2
    INDIC_CODES = {
        'en': 'eng_Latn',
        'hi': 'hin_Deva',
        'ta': 'tam_Taml',
        'te': 'tel_Telu',
        'kn': 'kan_Knda',
        'ml': 'mal_Mlym',
        'mr': 'mar_Deva',
        'gu': 'guj_Gujr',
        'bn': 'ben_Beng',
        'pa': 'pan_Guru',
        'ur': 'urd_Arab',
        'or': 'ory_Orya',
        'as': 'asm_Beng'
    }
    
    def __init__(self):
        """Initialize translator"""
        self.model = None
        self.tokenizer = None
        self._init_model()

    def _init_model(self):
        """Initialize IndicTrans2 model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            model_name = "ai4bharat/indic-trans_en-indic_1B"
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            logger.info("IndicTrans2 model loaded")
        except ImportError:
            logger.warning("IndicTrans2 not available, using fallback translation")
            self.model = None
            self.tokenizer = None
        except Exception as e:
            logger.warning(f"Could not load IndicTrans2: {e}, using fallback")
            self.model = None
            self.tokenizer = None

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, hi, ta, etc.)
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        # If source and target are same, return original
        if source_lang == target_lang:
            return text
        
        # Validate languages
        if source_lang not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported source language: {source_lang}")
            return text
        
        if target_lang not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported target language: {target_lang}")
            return text
        
        try:
            if self.model and self.tokenizer:
                return self._translate_indic(text, source_lang, target_lang)
            else:
                return self._fallback_translate(text, source_lang, target_lang)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def _translate_indic(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate using IndicTrans2
        
        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            Translated text
        """
        try:
            # Prepare input
            source_code = self.INDIC_CODES.get(source_lang, 'eng_Latn')
            target_code = self.INDIC_CODES.get(target_lang, 'eng_Latn')
            
            # Add language tags
            input_text = f"{source_code} {target_code} {text}"
            
            # Tokenize
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True
                )
            
            # Decode
            translated = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]
            
            return translated.strip()
        
        except Exception as e:
            logger.error(f"IndicTrans2 translation error: {e}")
            return text

    def _fallback_translate(self, text: str, source_lang: str, 
                           target_lang: str) -> str:
        """
        Fallback translation using simple rules
        Handles medical terminology common translations
        """
        # Common medical term translations
        medical_vocab = {
            ('en', 'hi'): {
                'patient': 'रोगी',
                'blood': 'रक्त',
                'heart': 'दिल',
                'temperature': 'तापमान',
                'fever': 'बुखार',
                'doctor': 'डॉक्टर',
                'hospital': 'अस्पताल',
                'medication': 'दवा'
            },
            ('en', 'ta'): {
                'patient': 'நோயாளி',
                'blood': 'இரத்தம்',
                'heart': 'இதயம்',
                'temperature': 'வெப்பநிலை',
                'fever': 'காய்ச்சல்',
                'doctor': 'மருத்துவர்',
                'hospital': 'மருத்துவமனை',
                'medication': 'மருந்து'
            }
        }
        
        # Try vocabulary lookup
        vocab_key = (source_lang, target_lang)
        if vocab_key in medical_vocab:
            vocab = medical_vocab[vocab_key]
            result = text
            for eng_word, trans_word in vocab.items():
                result = result.replace(eng_word, trans_word)
            return result
        
        # If no vocabulary, return original
        logger.warning(f"No fallback translation for {source_lang} -> {target_lang}")
        return text

    def detect_language(self, text: str) -> str:
        """
        Detect language of text
        Uses simple heuristics
        
        Args:
            text: Text to detect
            
        Returns:
            Language code
        """
        try:
            import langdetect
            lang = langdetect.detect(text)
            # Map to our language codes
            lang_mapping = {
                'hi': 'hi', 'ta': 'ta', 'te': 'te', 'kn': 'kn',
                'ml': 'ml', 'mr': 'mr', 'gu': 'gu', 'bn': 'bn',
                'pa': 'pa', 'ur': 'ur', 'or': 'or', 'as': 'as',
                'en': 'en'
            }
            return lang_mapping.get(lang, 'en')
        except:
            # Fallback: check for script
            return self._detect_by_script(text)

    def _detect_by_script(self, text: str) -> str:
        """
        Detect language by script detection
        """
        # Hindi/Marathi/Nepali (Devanagari)
        if any('\u0900' <= c <= '\u097F' for c in text):
            return 'hi'
        
        # Tamil
        if any('\u0B80' <= c <= '\u0BFF' for c in text):
            return 'ta'
        
        # Telugu
        if any('\u0C00' <= c <= '\u0C7F' for c in text):
            return 'te'
        
        # Kannada
        if any('\u0C80' <= c <= '\u0CFF' for c in text):
            return 'kn'
        
        # Malayalam
        if any('\u0D00' <= c <= '\u0D7F' for c in text):
            return 'ml'
        
        # Bengali
        if any('\u0B80' <= c <= '\u0BFF' for c in text):
            return 'bn'
        
        # Urdu (in Arabic script)
        if any('\u0600' <= c <= '\u06FF' for c in text):
            return 'ur'
        
        # Default to English
        return 'en'

    def batch_translate(self, texts: list, source_lang: str, 
                       target_lang: str) -> list:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            List of translated texts
        """
        return [
            self.translate(text, source_lang, target_lang)
            for text in texts
        ]


# Singleton instance
_translator = None


def get_translator():
    """Get or create translator instance"""
    global _translator
    if _translator is None:
        _translator = MultilingualTranslator()
    return _translator
