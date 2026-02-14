"""
BAAI BGE-M3 Multilingual Embedding Engine
Handles multilingual embeddings for medical documents and queries
"""

try:
    from FlagEmbedding import FlagModel
except ImportError:
    FlagModel = None

import numpy as np
import logging

logger = logging.getLogger(__name__)


class MultilingualEmbeddingEngine:
    """
    Uses BAAI BGE-M3 for multilingual embeddings
    Supports: English, Hindi, Tamil, Telugu, Kannada, Malayalam, etc.
    """
    
    def __init__(self):
        try:
            if FlagModel is not None:
                self.model = FlagModel(
                    "BAAI/bge-m3",
                    use_fp16=True,
                    query_instruction_for_retrieval="Represent this medical query for retrieval:"
                )
                self.model_loaded = True
            else:
                logger.warning("FlagEmbedding not available, using fallback")
                self.model = None
                self.model_loaded = False
        except Exception as e:
            logger.error(f"Error loading BGE-M3 model: {e}")
            self.model = None
            self.model_loaded = False

    def embed_text(self, text, language="en"):
        """
        Embed text in any language
        
        Args:
            text: Text to embed
            language: Language code (en, hi, ta, te, kn, ml, etc.)
            
        Returns:
            embedding vector
        """
        try:
            if not self.model_loaded or self.model is None:
                return self._fallback_embed(text)
            
            # BGE-M3 handles multilingual automatically
            embeddings = self.model.encode(
                [text],
                normalize_embeddings=True,
                convert_to_numpy=True
            )
            return embeddings[0]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return self._fallback_embed(text)

    def embed_batch(self, texts, is_query=False):
        """
        Embed multiple texts at once
        
        Args:
            texts: List of texts
            is_query: If True, applies query instruction
            
        Returns:
            List of embeddings
        """
        try:
            if not self.model_loaded or self.model is None:
                return [self._fallback_embed(t) for t in texts]
            
            if is_query:
                embeddings = self.model.encode_queries(texts, convert_to_numpy=True)
            else:
                embeddings = self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
            
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            return [self._fallback_embed(t) for t in texts]

    def _fallback_embed(self, text):
        """
        Fallback embedding using simple hash-based method
        """
        # Simple fallback: hash-based vector
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert bytes to float vector
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32) / 255.0
        # Normalize
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        # Pad/truncate to 384 dimensions (BGE-M3 default)
        if len(embedding) < 384:
            embedding = np.pad(embedding, (0, 384 - len(embedding)))
        else:
            embedding = embedding[:384]
        return embedding

    def similarity(self, embedding1, embedding2):
        """
        Calculate cosine similarity between two embeddings
        """
        return np.dot(embedding1, embedding2)

    def semantic_search(self, query_embedding, doc_embeddings, top_k=5):
        """
        Find most similar documents to query
        
        Args:
            query_embedding: Query embedding
            doc_embeddings: List of document embeddings
            top_k: Number of top results
            
        Returns:
            List of indices and scores
        """
        scores = [
            self.similarity(query_embedding, doc_emb) 
            for doc_emb in doc_embeddings
        ]
        top_indices = np.argsort(scores)[-top_k:][::-1]
        top_scores = [scores[i] for i in top_indices]
        return list(zip(top_indices, top_scores))


# Singleton instance
_embedding_engine = None


def get_embedding_engine():
    """Get or create embedding engine instance"""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = MultilingualEmbeddingEngine()
    return _embedding_engine
