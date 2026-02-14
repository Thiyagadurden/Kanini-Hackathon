"""
Sign Language Support System
Converts text to sign language representations and animations
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignGesture:
    """Represents a single sign gesture"""
    sign: str  # Sign name
    meaning: str  # What it represents
    hand_shape: str  # Hand configuration
    hand_position: str  # Position relative to body
    movement: str  # Type of movement
    duration_ms: int = 500  # Duration in milliseconds


class SignLanguageProcessor:
    """
    Converts text to sign language representations
    Supports International Sign Language (ISL) and Sign Supported Speech
    """
    
    # Common sign gestures
    SIGN_DICTIONARY = {
        # Greetings
        'hello': SignGesture('hello', 'greeting', 'open_hand', 'head_level', 'wave'),
        'goodbye': SignGesture('goodbye', 'farewell', 'open_hand', 'shoulder', 'wave_down'),
        'thank_you': SignGesture('thank_you', 'gratitude', 'open_hand', 'chest', 'move_away'),
        'please': SignGesture('please', 'polite_request', 'open_hand', 'chest', 'circular'),
        
        # Medical terms
        'patient': SignGesture('patient', 'person_receiving_care', 'point', 'forward', 'move_down'),
        'doctor': SignGesture('doctor', 'medical_professional', 'fingers_touch_chest', 'chest', 'move_forward'),
        'nurse': SignGesture('nurse', 'healthcare_provider', 'open_hand', 'arm', 'move_up'),
        'hospital': SignGesture('hospital', 'medical_facility', 'cross_hands', 'chest', 'sign_h'),
        'medicine': SignGesture('medicine', 'medication', 'pinch_hand', 'palm', 'move_circular'),
        'pain': SignGesture('pain', 'discomfort', 'point_fingers', 'body', 'quick_stab'),
        'help': SignGesture('help', 'assistance', 'open_hand', 'hip', 'lift_up'),
        'appointment': SignGesture('appointment', 'scheduled_meeting', 'point_hand', 'wrist', 'circle'),
        'prescription': SignGesture('prescription', 'medication_order', 'write_motion', 'palm', 'signed_motion'),
        
        # Common words
        'yes': SignGesture('yes', 'affirmative', 'hand_fist', 'shoulder', 'nod_down'),
        'no': SignGesture('no', 'negative', 'index_finger', 'head_level', 'side_to_side'),
        'water': SignGesture('water', 'liquid', 'w_hand', 'chin', 'move_down'),
        'food': SignGesture('food', 'nutrition', 'pinch_hand', 'mouth', 'move_to_mouth'),
        'rest': SignGesture('rest', 'sleep', 'both_hands_crossed', 'cheek', 'tilted'),
        'wait': SignGesture('wait', 'hold_time', 'both_hands_open', 'palm_up', 'hold_motion'),
        'time': SignGesture('time', 'duration', 'point_wrist', 'wrist', 'circular'),
        'day': SignGesture('day', 'daytime', 'finger_arm', 'head', 'arc_motion'),
        'good': SignGesture('good', 'positive', 'thumb_up', 'chest', 'move_up'),
        'bad': SignGesture('bad', 'negative', 'thumb_down', 'chest', 'move_down'),
    }
    
    # Common phrase templates for quick responses
    PHRASE_TEMPLATES = {
        'greeting': 'hello',
        'affirmative': 'yes',
        'negative': 'no',
        'gratitude': 'thank_you',
        'help_request': 'help',
        'farewell': 'goodbye',
    }
    
    def __init__(self):
        """Initialize sign language processor"""
        self.sign_dict = self.SIGN_DICTIONARY.copy()
    
    def text_to_signs(self, text: str) -> List[SignGesture]:
        """
        Convert text to sequence of sign gestures
        
        Args:
            text: Input text to convert
        
        Returns:
            List of SignGesture objects
        """
        # Clean and normalize text
        text = text.lower().strip()
        
        # Remove punctuation
        text = re.sub(r'[.,!?;:]', '', text)
        
        # Split into words
        words = text.split()
        
        # Convert words to signs
        signs = []
        for word in words:
            sign = self._get_sign_for_word(word)
            if sign:
                signs.append(sign)
        
        return signs
    
    def _get_sign_for_word(self, word: str) -> Optional[SignGesture]:
        """
        Get sign gesture for a word
        Common words are directly mapped, others are fingerspelled
        """
        word = word.lower().strip()
        
        # Direct mapping
        if word in self.sign_dict:
            return self.sign_dict[word]
        
        # Check for common suffixes/variations
        if word.endswith('ing'):
            base = word[:-3]
            if base in self.sign_dict:
                # Add continuous motion for -ing
                sign = self.sign_dict[base]
                sign.movement = 'continuous_' + sign.movement
                return sign
        
        # Fingerspell if not found
        return SignGesture(
            sign='fingerspell',
            meaning=word,
            hand_shape='spell_hand',
            hand_position='neutral',
            movement='sequential',
            duration_ms=len(word) * 100
        )
    
    def generate_animation_sequence(self, text: str) -> List[Dict]:
        """
        Generate animation sequence for frontend rendering
        
        Args:
            text: Text to convert to animations
        
        Returns:
            List of animation frames
        """
        signs = self.text_to_signs(text)
        animations = []
        
        current_time = 0
        for sign in signs:
            animation = {
                'sign': sign.sign,
                'meaning': sign.meaning,
                'hand_shape': sign.hand_shape,
                'hand_position': sign.hand_position,
                'movement': sign.movement,
                'start_time': current_time,
                'duration': sign.duration_ms,
                'end_time': current_time + sign.duration_ms,
            }
            animations.append(animation)
            current_time += sign.duration_ms + 100  # Add gap between signs
        
        return animations
    
    def get_video_references(self, text: str) -> List[Dict]:
        """
        Get references to video files for each gesture
        Can be integrated with sign language video libraries
        
        Args:
            text: Text to get video references for
        
        Returns:
            List of video references
        """
        signs = self.text_to_signs(text)
        videos = []
        
        for sign in signs:
            video_ref = {
                'sign': sign.sign,
                'video_id': f"{sign.sign}_{sign.hand_shape}",
                'url': f"/media/sign_language/{sign.sign}.mp4",
                'description': sign.meaning,
            }
            videos.append(video_ref)
        
        return videos
    
    def add_custom_sign(self, word: str, gesture: SignGesture) -> None:
        """
        Add custom sign gesture mapping
        
        Args:
            word: Word to map
            gesture: SignGesture definition
        """
        self.sign_dict[word.lower()] = gesture
        logger.info(f"Added custom sign mapping for '{word}'")
    
    def get_common_medical_signs(self) -> Dict[str, SignGesture]:
        """Get all medical-related signs"""
        medical_signs = {}
        medical_words = [
            'patient', 'doctor', 'nurse', 'hospital', 'medicine',
            'pain', 'help', 'appointment', 'prescription'
        ]
        
        for word in medical_words:
            if word in self.sign_dict:
                medical_signs[word] = self.sign_dict[word]
        
        return medical_signs


class SignLanguageAPI:
    """
    API wrapper for sign language functionality
    Integrates with web/mobile frontends
    """
    
    def __init__(self):
        """Initialize sign language API"""
        self.processor = SignLanguageProcessor()
    
    def convert_to_sign(self, text: str, output_format: str = 'animations') -> Dict:
        """
        Convert text to sign language representation
        
        Args:
            text: Text to convert
            output_format: 'animations', 'videos', or 'hybrid'
        
        Returns:
            Dictionary with sign language data
        """
        result = {
            'original_text': text,
            'format': output_format,
            'timestamp': self._get_timestamp(),
        }
        
        if output_format in ['animations', 'hybrid']:
            result['animations'] = self.processor.generate_animation_sequence(text)
        
        if output_format in ['videos', 'hybrid']:
            result['videos'] = self.processor.get_video_references(text)
        
        signs = self.processor.text_to_signs(text)
        result['total_signs'] = len(signs)
        result['total_duration_ms'] = sum(s.duration_ms for s in signs) + (len(signs) * 100)
        
        return result
    
    def get_medical_glossary(self) -> Dict[str, Dict]:
        """Get medical terms in sign language"""
        medical_signs = self.processor.get_common_medical_signs()
        
        glossary = {}
        for word, gesture in medical_signs.items():
            glossary[word] = {
                'sign': gesture.sign,
                'meaning': gesture.meaning,
                'hand_shape': gesture.hand_shape,
                'hand_position': gesture.hand_position,
                'movement': gesture.movement,
            }
        
        return glossary
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def batch_convert(self, texts: List[str], output_format: str = 'animations') -> List[Dict]:
        """Convert multiple texts"""
        return [self.convert_to_sign(text, output_format) for text in texts]


# Global instance
_sign_language_api = None

def get_sign_language_api() -> SignLanguageAPI:
    """Get or create global SignLanguageAPI instance"""
    global _sign_language_api
    if _sign_language_api is None:
        _sign_language_api = SignLanguageAPI()
    return _sign_language_api

def text_to_sign(text: str, output_format: str = 'animations') -> Dict:
    """Convenience function for text-to-sign conversion"""
    api = get_sign_language_api()
    return api.convert_to_sign(text, output_format)
