"""
Unified Medical AI Pipeline
Orchestrates: Document Loading -> Embeddings -> RAG -> Mistral LLM -> XGBoost Prediction
Supports multilingual input: English, Hindi, Tamil, Telugu, Kannada, Malayalam
"""

import os
import json
import logging
from typing import Dict, List, Optional

# Import components
from embedding_engine import get_embedding_engine
from mistral_engine import get_mistral_engine
from xgboost_predictor import get_predictor
from rag_database import get_rag_pipeline
from apps.accessibility.services.translation_service import get_translator

logger = logging.getLogger(__name__)


class UnifiedMedicalAIPipeline:
    """
    Complete AI pipeline for medical diagnosis and risk prediction
    
    Flow:
    1. Document Loading (PDF/Text/User Input)
    2. Language Detection & Translation (IndicTrans2)
    3. Embedding (BAAI bge-m3)
    4. Vector Database Retrieval (RAG)
    5. Mistral LLM (Structured Extraction)
    6. XGBoost (Risk Prediction)
    7. Explanation Generation (Mistral)
    8. Output Translation
    """
    
    def __init__(self, mistral_api_key):
        """
        Initialize unified pipeline
        
        Args:
            mistral_api_key: Mistral API key from environment
        """
        self.embedding_engine = get_embedding_engine()
        self.mistral_engine = get_mistral_engine(mistral_api_key)
        self.predictor = get_predictor()
        self.rag_pipeline = get_rag_pipeline()
        self.translator = get_translator()
        
        logger.info("Initialized unified medical AI pipeline")

    def process_document(self, document_text: str, doc_type: str = "ehr", 
                        patient_id: str = "", language: str = "en") -> Dict:
        """
        Process medical document through full pipeline
        
        Args:
            document_text: Document content
            doc_type: Type of document (ehr, note, lab, pdf, etc.)
            patient_id: Patient identifier
            language: Input language code
            
        Returns:
            Processed results with extraction and predictions
        """
        try:
            logger.info(f"Processing {doc_type} document for patient {patient_id}")
            
            # Step 1: Detect/handle language
            if language != "en":
                translated_text = self.translator.translate(
                    document_text, language, "en"
                )
                work_text = translated_text
                original_text = document_text
            else:
                work_text = document_text
                original_text = document_text
            
            # Step 2: Add to RAG pipeline
            chunk_count = self.rag_pipeline.add_ehr_document(
                work_text, patient_id, source=doc_type
            )
            
            # Step 3: Extract structured data using Mistral
            extracted = self.mistral_engine.extract_from_text(work_text, language)
            
            # Step 4: Prepare patient data for prediction
            patient_data = self._prepare_patient_data(extracted)
            
            # Step 5: Predict risk using XGBoost
            risk_prediction = self.predictor.predict_risk(patient_data)
            
            # Step 6: Generate explanation
            explanation = self.mistral_engine.generate_explanation(
                risk_prediction['risk_score'],
                [f['feature'] for f in risk_prediction['top_risk_factors']],
                patient_data,
                language
            )
            
            # Step 7: Translate explanation back if needed
            if language != "en":
                explanation = self.translator.translate(
                    explanation, "en", language
                )
            
            return {
                'status': 'success',
                'document_type': doc_type,
                'patient_id': patient_id,
                'chunks_processed': chunk_count,
                'extracted_data': extracted,
                'risk_prediction': risk_prediction,
                'explanation': explanation,
                'language': language
            }
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'patient_id': patient_id
            }

    def process_user_input(self, user_text: str, language: str = "en") -> Dict:
        """
        Process user input query (dashboard interaction)
        
        Args:
            user_text: User input text
            language: Input language
            
        Returns:
            Response with relevant information and predictions
        """
        try:
            logger.info(f"Processing user input in {language}")
            
            # Translate to English for processing
            if language != "en":
                work_text = self.translator.translate(user_text, language, "en")
            else:
                work_text = user_text
            
            # Retrieve relevant context from RAG
            context = self.rag_pipeline.retrieve_context(work_text, top_k=3)
            
            # Generate answer using Mistral
            answer = self.mistral_engine.answer_clinical_question(
                work_text, context, language
            )
            
            # Translate back if needed
            if language != "en":
                answer = self.translator.translate(answer, "en", language)
            
            return {
                'status': 'success',
                'query': user_text,
                'answer': answer,
                'context_sources': len(context.split('\n\n')),
                'language': language
            }
        
        except Exception as e:
            logger.error(f"User input processing error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'query': user_text
            }

    def predict_from_vitals(self, vital_signs: Dict, 
                           medical_history: List = None,
                           language: str = "en") -> Dict:
        """
        Quick risk prediction from vital signs
        
        Args:
            vital_signs: Dictionary of vital measurements
            medical_history: List of medical conditions
            language: Output language
            
        Returns:
            Risk prediction with explanation
        """
        try:
            # Prepare patient data
            patient_data = {
                **vital_signs,
                'comorbidity_count': len(medical_history or []),
                'medical_history': medical_history or []
            }
            
            # Predict
            risk = self.predictor.predict_risk(patient_data)
            
            # Generate explanation
            explanation = self.mistral_engine.generate_explanation(
                risk['risk_score'],
                [f['feature'] for f in risk['top_risk_factors']],
                patient_data,
                language
            )
            
            # Translate if needed
            if language != "en":
                explanation = self.translator.translate(
                    explanation, "en", language
                )
            
            return {
                'status': 'success',
                'risk_prediction': risk,
                'explanation': explanation,
                'language': language
            }
        
        except Exception as e:
            logger.error(f"Vitals prediction error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _prepare_patient_data(self, extracted_data: Dict) -> Dict:
        """
        Prepare extracted data for XGBoost prediction
        
        Args:
            extracted_data: Data extracted by Mistral
            
        Returns:
            Formatted patient data for prediction
        """
        vital_signs = extracted_data.get('vital_signs', {})
        
        patient_data = {
            'age': extracted_data.get('age', 50),
            'heart_rate': vital_signs.get('heart_rate', 70),
            'systolic_bp': vital_signs.get('systolic_bp', 120),
            'diastolic_bp': vital_signs.get('diastolic_bp', 80),
            'temperature': vital_signs.get('temperature', 37),
            'spo2': vital_signs.get('spo2', 98),
            'respiratory_rate': vital_signs.get('respiratory_rate', 16),
            'glucose': vital_signs.get('glucose', 100),
            'comorbidity_count': len(extracted_data.get('medical_history', [])),
            'medication_count': len(extracted_data.get('current_medications', [])),
            'previous_hospitalizations': 0,
            'days_since_last_visit': 0,
            'abnormal_lab_count': 0
        }
        
        return patient_data

    def process_pdf_content(self, pdf_text: str, patient_id: str = "",
                           language: str = "en") -> Dict:
        """
        Process extracted PDF content
        
        Args:
            pdf_text: Text extracted from PDF
            patient_id: Patient ID
            language: Document language
            
        Returns:
            Processed results
        """
        return self.process_document(
            pdf_text, "pdf", patient_id, language
        )

    def get_patient_summary(self, patient_id: str, language: str = "en") -> Dict:
        """
        Get comprehensive patient summary
        
        Args:
            patient_id: Patient ID
            language: Output language
            
        Returns:
            Patient summary
        """
        try:
            # Retrieve all patient documents from RAG
            patient_docs = [
                doc for doc in self.rag_pipeline.vector_db.metadata
                if doc.get('metadata', {}).get('patient_id') == patient_id
            ]
            
            if not patient_docs:
                return {
                    'status': 'no_data',
                    'patient_id': patient_id,
                    'message': 'No documents found for patient'
                }
            
            # Combine all documents
            all_text = "\n".join([
                self.rag_pipeline.vector_db.documents[doc['id']]
                for doc in patient_docs
            ])
            
            # Generate summary
            summary = self.mistral_engine.summarize_patient_record(
                {'documents': all_text}, language
            )
            
            return {
                'status': 'success',
                'patient_id': patient_id,
                'document_count': len(patient_docs),
                'summary': summary,
                'language': language
            }
        
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'patient_id': patient_id
            }


# Singleton pipeline instance
_pipeline = None


def get_pipeline(mistral_api_key: Optional[str] = None):
    """
    Get or create unified pipeline
    
    Args:
        mistral_api_key: Mistral API key (optional, can come from env)
        
    Returns:
        UnifiedMedicalAIPipeline instance
    """
    global _pipeline
    
    if _pipeline is None:
        if mistral_api_key is None:
            mistral_api_key = os.getenv('MISTRAL_API_KEY')
        
        if not mistral_api_key:
            raise ValueError("MISTRAL_API_KEY required")
        
        _pipeline = UnifiedMedicalAIPipeline(mistral_api_key)
    
    return _pipeline
