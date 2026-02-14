"""
Mistral LLM Engine for Medical AI
Handles language understanding, explanations, and structured extraction
Supports multilingual input: English, Hindi, Tamil, Telugu, Kannada, Malayalam
"""

from mistralai import Mistral
import json
import logging

logger = logging.getLogger(__name__)


class MistralMedicalEngine:
    """
    Mistral-based LLM for medical AI
    - Natural language understanding
    - Structured data extraction
    - Clinical explanations
    - Multilingual support
    """
    
    def __init__(self, api_key):
        """Initialize Mistral client"""
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-small"
        self.language_map = {
            'en': 'English',
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'gu': 'Gujarati'
        }

    def extract_from_text(self, text, language="en"):
        """
        Extract structured medical information from unstructured text
        
        Args:
            text: Input text (EHR, patient note, etc.)
            language: Language code
            
        Returns:
            Structured JSON with extracted data
        """
        prompt = f"""Extract medical information from this {self.language_map.get(language, 'English')} text.
Return ONLY valid JSON with this structure:
{{
    "symptoms": [],
    "vital_signs": {{}},
    "medical_history": [],
    "allergies": [],
    "current_medications": [],
    "risk_factors": []
}}

Text: {text}

JSON Response:"""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                return extracted
            return {"raw_response": response_text}
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return {"error": str(e)}

    def generate_explanation(self, risk_score, risk_factors, patient_data, language="en"):
        """
        Generate clinical explanation for risk prediction
        
        Args:
            risk_score: Predicted risk score (0-1)
            risk_factors: List of contributing factors
            patient_data: Patient information
            language: Output language code
            
        Returns:
            Clinical explanation string
        """
        lang_name = self.language_map.get(language, 'English')
        
        prompt = f"""As a medical AI, explain this patient risk assessment in {lang_name}.

Patient Data:
- Age: {patient_data.get('age')}
- Vital Signs: {patient_data.get('vital_signs', {{}})}
- Medical History: {patient_data.get('medical_history', [])}

Risk Assessment:
- Risk Score: {risk_score:.2%}
- Contributing Factors: {', '.join(risk_factors)}

Provide a clear, professional explanation suitable for healthcare providers.
Use only {lang_name} language.
Keep it concise (2-3 sentences)."""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            return f"Unable to generate explanation: {str(e)}"

    def extract_from_pdf_context(self, pdf_text, language="en"):
        """
        Extract medical data from PDF document text
        
        Args:
            pdf_text: Text extracted from PDF
            language: Language of input
            
        Returns:
            Structured medical data
        """
        prompt = f"""Analyze this medical document and extract key information.
Document:
{pdf_text[:2000]}

Extract and structure:
1. Patient demographics
2. Chief complaints/symptoms
3. Vital signs
4. Lab results
5. Medications
6. Allergies
7. Medical history
8. Risk indicators

Return as JSON."""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            response_text = response.choices[0].message.content.strip()
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw_text": response_text}
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return {"error": str(e)}

    def answer_clinical_question(self, question, context, language="en"):
        """
        Answer clinical questions based on context
        
        Args:
            question: Clinical question
            context: Relevant clinical context/RAG results
            language: Output language
            
        Returns:
            Clinical answer
        """
        lang_name = self.language_map.get(language, 'English')
        
        prompt = f"""Answer this clinical question based on the provided context.
Use {lang_name} language in your response.
Be concise and evidence-based.

Context:
{context}

Question: {question}

Answer:"""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Question answering error: {e}")
            return f"Unable to answer: {str(e)}"

    def summarize_patient_record(self, patient_record, language="en"):
        """
        Generate concise patient summary
        
        Args:
            patient_record: Full patient record data
            language: Output language
            
        Returns:
            Structured summary
        """
        lang_name = self.language_map.get(language, 'English')
        
        prompt = f"""Summarize this patient record in {lang_name}.
Provide:
1. Chief complaint
2. Key vitals
3. Notable history
4. Current medications
5. Risk summary

Patient Record:
{json.dumps(patient_record, indent=2)[:1500]}

Summary:"""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return str(e)


# Factory function
def get_mistral_engine(api_key):
    """Create Mistral engine instance"""
    return MistralMedicalEngine(api_key)
