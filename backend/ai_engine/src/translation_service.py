"""
Multilingual Translation Service using IndicTrans2
Supports translation between 22 Indian languages and English
"""

import torch
from typing import List, Dict, Optional, Tuple
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

# Language codes mapping
LANGUAGE_CODES = {
    'hindi': 'hin_Deva',
    'tamil': 'tam_Taml',
    'telugu': 'tel_Telu',
    'kannada': 'kan_Knda',
    'malayalam': 'mal_Mlym',
    'marathi': 'mar_Deva',
    'gujarati': 'guj_Gujr',
    'bengali': 'ben_Beng',
    'punjabi': 'pan_Guru',
    'urdu': 'urd_Arab',
    'english': 'eng_Latn',
    'odia': 'ory_Orya',
    'assamese': 'asm_Beng',
    'kashmiri': 'kas_Arab',
}

# Language names for display
LANGUAGE_NAMES = {
    'hindi': 'हिंदी (Hindi)',
    'tamil': 'தமிழ் (Tamil)',
    'telugu': 'తెలుగు (Telugu)',
    'kannada': 'ಕನ್ನಡ (Kannada)',
    'malayalam': 'മലയാളം (Malayalam)',
    'marathi': 'मराठी (Marathi)',
    'gujarati': 'ગુજરાતી (Gujarati)',
    'bengali': 'বাংলা (Bengali)',
    'punjabi': 'ਪੰਜਾਬੀ (Punjabi)',
    'urdu': 'اردو (Urdu)',
    'english': 'English',
    'odia': 'ଓଡ଼ିଆ (Odia)',
    'assamese': 'অসমীয়া (Assamese)',
    'kashmiri': 'کاشُر (Kashmiri)',
}


class MultilingualTranslator:
    """
    Handles multilingual translation using IndicTrans2 model
    Supports 22 Indian languages and English
    """
    
    def __init__(self, model_name: str = "ai4bharat/indictrans2-indic-en-1B", 
                 device: Optional[str] = None, use_gpu: bool = True):
        """
        Initialize the multilingual translator
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cuda' or 'cpu')
            use_gpu: Whether to attempt GPU usage
        """
        self.device = device or ("cuda" if (use_gpu and torch.cuda.is_available()) else "cpu")
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.initialized = False
        
        logger.info(f"Initializing MultilingualTranslator on device: {self.device}")
    
    def initialize(self) -> bool:
        """
        Load model and tokenizer (lazy initialization)
        Returns True if successful, False otherwise
        """
        try:
            if self.initialized:
                return True
            
            logger.info(f"Loading tokenizer from {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                trust_remote_code=True
            )
            
            logger.info(f"Loading model from {self.model_name}...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                attn_implementation="flash_attention_2" if self._has_flash_attn() else None
            ).to(self.device)
            
            self.initialized = True
            logger.info("Translation model initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing translation model: {str(e)}")
            self.initialized = False
            return False
    
    @staticmethod
    def _has_flash_attn() -> bool:
        """Check if flash_attention is available"""
        try:
            import flash_attn
            return True
        except ImportError:
            return False
    
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> Optional[str]:
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            src_lang: Source language code
            tgt_lang: Target language code
        
        Returns:
            Translated text or None if translation fails
        """
        if not self.initialized:
            if not self.initialize():
                return None
        
        try:
            src_code = LANGUAGE_CODES.get(src_lang.lower())
            tgt_code = LANGUAGE_CODES.get(tgt_lang.lower())
            
            if not src_code or not tgt_code:
                logger.error(f"Unsupported language: {src_lang} or {tgt_lang}")
                return None
            
            if src_lang.lower() == tgt_lang.lower():
                return text
            
            # Preprocess with IndicProcessor if available
            batch = [text]
            
            try:
                from IndicTransToolkit.processor import IndicProcessor
                ip = IndicProcessor(inference=True)
                batch = ip.preprocess_batch([text], src_lang=src_code, tgt_lang=tgt_code)
            except ImportError:
                logger.warning("IndicProcessor not available, using raw text")
            
            # Tokenize
            inputs = self.tokenizer(
                batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                )
            
            # Decode
            translations = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            
            # Postprocess
            result = translations[0]
            try:
                from IndicTransToolkit.processor import IndicProcessor
                ip = IndicProcessor(inference=True)
                result = ip.postprocess_batch([result], lang=tgt_code)[0]
            except ImportError:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None
    
    def batch_translate(self, texts: List[str], src_lang: str, tgt_lang: str) -> List[str]:
        """
        Translate multiple texts at once
        
        Args:
            texts: List of texts to translate
            src_lang: Source language code
            tgt_lang: Target language code
        
        Returns:
            List of translated texts
        """
        if not self.initialized:
            if not self.initialize():
                return texts
        
        results = []
        for text in texts:
            translated = self.translate(text, src_lang, tgt_lang)
            results.append(translated or text)
        
        return results
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return LANGUAGE_CODES.copy()
    
    def get_language_names(self) -> Dict[str, str]:
        """Get language names for UI display"""
        return LANGUAGE_NAMES.copy()


class LanguageDetector:
    """
    Simple language detection based on character sets
    """
    
    # Unicode ranges for different scripts
    SCRIPT_RANGES = {
        'hindi': (0x0900, 0x097F),
        'tamil': (0x0B80, 0x0BFF),
        'telugu': (0x0C00, 0x0C7F),
        'kannada': (0x0C80, 0x0CFF),
        'malayalam': (0x0D00, 0x0D7F),
        'marathi': (0x0900, 0x097F),  # Uses Devanagari
        'gujarati': (0x0A80, 0x0AFF),
        'bengali': (0x0980, 0x09FF),
        'punjabi': (0x0A00, 0x0A7F),
        'english': (0x0041, 0x005A),  # A-Z
    }
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language based on character set
        
        Args:
            text: Text to detect
        
        Returns:
            Language code
        """
        if not text:
            return 'english'
        
        # Count characters in each script
        script_counts = {lang: 0 for lang in LanguageDetector.SCRIPT_RANGES}
        
        for char in text:
            char_code = ord(char)
            for lang, (start, end) in LanguageDetector.SCRIPT_RANGES.items():
                if start <= char_code <= end:
                    script_counts[lang] += 1
        
        # Find language with most matches
        detected = max(script_counts, key=script_counts.get)
        return detected if script_counts[detected] > 0 else 'english'
    
    @staticmethod
    def is_hindi(text: str) -> bool:
        """Check if text is in Hindi"""
        return LanguageDetector.detect_language(text) == 'hindi'
    
    @staticmethod
    def is_english(text: str) -> bool:
        """Check if text is in English"""
        return LanguageDetector.detect_language(text) == 'english'


# Global translator instance (lazy loaded)
_translator = None

def get_translator() -> MultilingualTranslator:
    """Get or create global translator instance"""
    global _translator
    if _translator is None:
        _translator = MultilingualTranslator()
    return _translator

def translate(text: str, src_lang: str, tgt_lang: str) -> Optional[str]:
    """Convenience function for translation"""
    translator = get_translator()
    return translator.translate(text, src_lang, tgt_lang)

def detect_language(text: str) -> str:
    """Convenience function for language detection"""
    return LanguageDetector.detect_language(text)
