from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from ai_engine.src.inference import InferenceEngine
import os
import logging

logger = logging.getLogger(__name__)

# Initialize engines
engine = InferenceEngine()

# Initialize unified AI pipeline
try:
    from unified_ai_pipeline import get_pipeline
    mistral_key = os.getenv('MISTRAL_API_KEY')
    ai_pipeline = get_pipeline(mistral_key) if mistral_key else None
except Exception as e:
    logger.warning(f"Could not initialize unified AI pipeline: {e}")
    ai_pipeline = None


@api_view(['POST'])
@permission_classes([AllowAny]) # Change to IsAuthenticated in production
def predict_risk(request):
    """
    Predict risk level using XGBoost and Mistral
    Supports multilingual input (English, Hindi, Tamil, Telugu, Kannada, Malayalam)
    """
    try:
        data = request.data
        language = data.get('language', 'en')
        
        # Use unified pipeline if available
        if ai_pipeline:
            vital_signs = {
                'age': data.get('age', 50),
                'heart_rate': data.get('heart_rate', 70),
                'systolic_bp': data.get('systolic_bp', 120),
                'diastolic_bp': data.get('diastolic_bp', 80),
                'temperature': data.get('temperature', 37),
                'spo2': data.get('spo2', 98),
                'respiratory_rate': data.get('respiratory_rate', 16),
                'glucose': data.get('glucose', 100),
            }
            
            medical_history = data.get('medical_history', [])
            
            result = ai_pipeline.predict_from_vitals(
                vital_signs,
                medical_history,
                language
            )
            
            return Response(result, status=status.HTTP_200_OK)
        
        else:
            # Fallback to original engine
            required_fields = ['age', 'gender', 'symptom_chest_pain', 'heart_rate']
            for field in required_fields:
                if field not in data:
                    return Response({"error": f"Missing field: {field}"}, status=status.HTTP_400_BAD_REQUEST)
            
            result = engine.predict(data)
            return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return Response(
            {"error": "Internal Server Error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def process_document(request):
    """
    Process medical document (EHR, PDF, Notes)
    Extracts structured data, predicts risk, generates explanation
    Supports Tamil, Hindi, English, Telugu, Kannada, Malayalam input
    """
    try:
        if not ai_pipeline:
            return Response(
                {"error": "AI pipeline not available"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        document = request.data.get('document', '')
        doc_type = request.data.get('type', 'ehr')
        patient_id = request.data.get('patient_id', '')
        language = request.data.get('language', 'en')
        
        if not document:
            return Response(
                {"error": "Document required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = ai_pipeline.process_document(
            document, doc_type, patient_id, language
        )
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Document processing error: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def query_pipeline(request):
    """
    Process user queries with RAG and Mistral LLM
    Supports multilingual input
    """
    try:
        if not ai_pipeline:
            return Response(
                {"error": "AI pipeline not available"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        query = request.data.get('query', '')
        language = request.data.get('language', 'en')
        
        if not query:
            return Response(
                {"error": "Query required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = ai_pipeline.process_user_input(query, language)
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def explain_prediction(request):
    """
    Explain a prediction with Mistral LLM
    """
    try:
        if not ai_pipeline:
            return Response(
                {"message": "Explanation included in /predict response"},
                status=status.HTTP_200_OK
            )
        
        risk_score = request.data.get('risk_score', 0.5)
        risk_factors = request.data.get('risk_factors', [])
        patient_data = request.data.get('patient_data', {})
        language = request.data.get('language', 'en')
        
        explanation = ai_pipeline.mistral_engine.generate_explanation(
            risk_score, risk_factors, patient_data, language
        )
        
        return Response(
            {"explanation": explanation, "language": language},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def retrieve_context(request):
    """
    Retrieve medical context for a query using RAG and BAAI embeddings
    """
    try:
        if not ai_pipeline:
            return Response(
                {"error": "AI pipeline not available"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        query = request.query_params.get('query', '')
        top_k = int(request.query_params.get('top_k', 3))
        
        if not query:
            return Response(
                {"error": "Query required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        context = ai_pipeline.rag_pipeline.retrieve_context(query, top_k)
        
        return Response(
            {"context": context, "query": query},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Context retrieval error: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
