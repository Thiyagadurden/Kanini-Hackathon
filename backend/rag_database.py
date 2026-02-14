"""
RAG Pipeline with Vector Database
Retrieval-Augmented Generation for medical context
Uses FAISS for fast similarity search
"""

import numpy as np
import json
import logging
from datetime import datetime
from embedding_engine import get_embedding_engine

logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    In-memory vector database with FAISS
    Stores medical documents and enables semantic search
    """
    
    def __init__(self):
        """Initialize vector database"""
        try:
            import faiss
            self.faiss = faiss
            self.use_faiss = True
        except ImportError:
            logger.warning("FAISS not available, using simple search")
            self.use_faiss = False
        
        self.embeddings_engine = get_embedding_engine()
        self.documents = []
        self.embeddings = []
        self.index = None
        self.metadata = []

    def add_document(self, text, doc_type="medical", source="", metadata=None):
        """
        Add document to vector database
        
        Args:
            text: Document text
            doc_type: Type of document (medical, lab, note, etc.)
            source: Source of document
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            # Embed document
            embedding = self.embeddings_engine.embed_text(text)
            
            doc_id = len(self.documents)
            self.documents.append(text)
            self.embeddings.append(embedding)
            
            # Store metadata
            doc_metadata = {
                'id': doc_id,
                'type': doc_type,
                'source': source,
                'timestamp': datetime.now().isoformat(),
                'length': len(text),
                'metadata': metadata or {}
            }
            self.metadata.append(doc_metadata)
            
            # Rebuild index
            self._build_index()
            
            logger.info(f"Added document {doc_id}: {source}")
            return doc_id
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return None

    def add_batch(self, documents):
        """
        Add multiple documents
        
        Args:
            documents: List of {'text': '', 'type': '', 'source': '', 'metadata': {}}
        """
        for doc in documents:
            self.add_document(
                doc.get('text', ''),
                doc.get('type', 'medical'),
                doc.get('source', ''),
                doc.get('metadata')
            )

    def _build_index(self):
        """Build FAISS index from embeddings"""
        if not self.embeddings:
            return
        
        try:
            if self.use_faiss:
                embeddings_array = np.array(self.embeddings).astype(np.float32)
                dimension = embeddings_array.shape[1]
                
                self.index = self.faiss.IndexFlatL2(dimension)
                self.index.add(embeddings_array)
            else:
                self.index = None
        except Exception as e:
            logger.warning(f"Could not build FAISS index: {e}")
            self.use_faiss = False

    def search(self, query, top_k=5, doc_type_filter=None):
        """
        Search for similar documents
        
        Args:
            query: Query text
            top_k: Number of results
            doc_type_filter: Filter by document type
            
        Returns:
            List of relevant documents with scores
        """
        try:
            if not self.embeddings:
                return []
            
            # Embed query
            query_embedding = self.embeddings_engine.embed_text(query)
            
            if self.use_faiss and self.index:
                # FAISS search
                query_array = np.array([query_embedding]).astype(np.float32)
                distances, indices = self.index.search(query_array, min(top_k * 2, len(self.embeddings)))
                
                results = []
                for idx, distance in zip(indices[0], distances[0]):
                    if idx < len(self.documents):
                        doc_meta = self.metadata[idx]
                        
                        # Filter by type if specified
                        if doc_type_filter and doc_meta['type'] != doc_type_filter:
                            continue
                        
                        # Convert L2 distance to similarity score
                        similarity = 1 / (1 + distance)
                        
                        results.append({
                            'id': idx,
                            'text': self.documents[idx][:500],  # First 500 chars
                            'full_text': self.documents[idx],
                            'similarity': similarity,
                            'metadata': doc_meta
                        })
                
                return results[:top_k]
            else:
                # Fallback: simple similarity search
                return self._simple_search(query_embedding, top_k, doc_type_filter)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def _simple_search(self, query_embedding, top_k, doc_type_filter):
        """Fallback simple search"""
        scores = []
        for i, doc_emb in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, doc_emb)
            
            doc_meta = self.metadata[i]
            if doc_type_filter and doc_meta['type'] != doc_type_filter:
                continue
            
            scores.append((i, similarity))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in scores[:top_k]:
            doc_meta = self.metadata[idx]
            results.append({
                'id': idx,
                'text': self.documents[idx][:500],
                'full_text': self.documents[idx],
                'similarity': max(0, score),  # Normalize
                'metadata': doc_meta
            })
        
        return results

    def get_context(self, query, top_k=3):
        """
        Get context for RAG
        
        Args:
            query: Query text
            top_k: Number of documents
            
        Returns:
            Concatenated context string
        """
        results = self.search(query, top_k)
        context = "\n\n".join([
            f"[{r['metadata']['type'].upper()} - Score: {r['similarity']:.2f}]\n{r['full_text']}"
            for r in results
        ])
        return context

    def clear(self):
        """Clear database"""
        self.documents = []
        self.embeddings = []
        self.metadata = []
        self.index = None


class RAGPipeline:
    """
    Complete RAG pipeline
    Document -> Chunks -> Embeddings -> Vector DB -> Retrieval -> LLM
    """
    
    def __init__(self):
        """Initialize RAG pipeline"""
        self.vector_db = VectorDatabase()
        self.chunk_size = 500
        self.chunk_overlap = 50

    def add_ehr_document(self, document_text, patient_id="", source="EHR"):
        """
        Add EHR document to pipeline
        
        Args:
            document_text: Full EHR text
            patient_id: Patient identifier
            source: Source of document
            
        Returns:
            Number of chunks created
        """
        # Split into chunks
        chunks = self._chunk_text(document_text)
        
        count = 0
        for i, chunk in enumerate(chunks):
            doc_id = self.vector_db.add_document(
                chunk,
                doc_type="ehr",
                source=source,
                metadata={
                    'patient_id': patient_id,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            )
            if doc_id is not None:
                count += 1
        
        logger.info(f"Processed EHR into {count} chunks")
        return count

    def add_lab_results(self, lab_data, patient_id=""):
        """
        Add lab results as document
        
        Args:
            lab_data: Lab results dictionary
            patient_id: Patient ID
        """
        text = json.dumps(lab_data, indent=2)
        self.vector_db.add_document(
            text,
            doc_type="lab",
            source="lab_results",
            metadata={'patient_id': patient_id}
        )

    def add_medications(self, medications, patient_id=""):
        """Add medication list"""
        text = "Medications:\n" + "\n".join([
            f"- {med.get('name', '')}: {med.get('dose', '')} {med.get('frequency', '')}"
            for med in medications
        ])
        self.vector_db.add_document(
            text,
            doc_type="medications",
            source="medication_list",
            metadata={'patient_id': patient_id}
        )

    def retrieve_context(self, query, top_k=3):
        """
        Retrieve relevant context for query
        
        Args:
            query: Query text
            top_k: Number of results
            
        Returns:
            Context string ready for LLM
        """
        return self.vector_db.get_context(query, top_k)

    def _chunk_text(self, text):
        """
        Split text into overlapping chunks
        
        Args:
            text: Full text
            
        Returns:
            List of chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap
        
        return chunks

    def clear(self):
        """Clear pipeline"""
        self.vector_db.clear()


# Singleton instance
_rag_pipeline = None


def get_rag_pipeline():
    """Get or create RAG pipeline"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
