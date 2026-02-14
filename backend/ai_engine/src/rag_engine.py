import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer

VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), '../data/faiss_index.bin')
DOCS_PATH = os.path.join(os.path.dirname(__file__), '../data/docs.pkl')

class MedicalRAG:
    def __init__(self):
        self.model = None
        self.index = None
        self.documents = []
        
        # Dummy medical knowledge base
        self.knowledge_base = [
            # Cardiology
            "Chest pain with radiation to the left arm is a classic sign of myocardial infarction (heart attack). Immediate ECG and Troponin levels required.",
            "Stable angina usually occurs with exertion and is relieved by rest or nitroglycerin.",
            "Hypertension urgency is defined as BP > 180/120 without end-organ damage.",
            
            # Pulmonology
            "Asthma exacerbation presents with wheezing, dyspnea, and cough. Treatment includes SABA and corticosteroids.",
            "Pneumonia symptoms include fever, cough with phlegm, and difficulty breathing. Chest X-ray confirms consolidation.",
            "Chronic Obstructive Pulmonary Disease (COPD) is characterized by chronic airflow limitation that is not fully reversible.",
            
            # Neurology
            "Stroke symptoms (FAST): Face drooping, Arm weakness, Speech difficulty, Time to call emergency.",
            "Migraine headaches are often unilateral, pulsating, and associated with nausea/vomiting and photophobia.",
            
            # General / Infection
            "Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. Look for SOFA score > 2.",
            "Diabetes Mellitus Type 2 presents with polyuria, polydipsia, and unexplained weight loss. HbA1c > 6.5%.",
            
            # Emergency Protocols
            "Triage Level 1 (Resuscitation): Immediate threat to life (e.g., cardiac arrest, major trauma).",
            "Triage Level 2 (Emergent): Potential threat to life or limb (e.g., chest pain, stroke symptoms).",
            "Triage Level 3 (Urgent): Condition could progress to emergency (e.g., abdominal pain, high fever).",
        ]

    def build_index(self):
        print("Building vector index...")
        if self.model is None:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = self.knowledge_base
        embeddings = self.model.encode(self.documents)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save index and docs
        faiss.write_index(self.index, VECTOR_DB_PATH)
        with open(DOCS_PATH, 'wb') as f:
            pickle.dump(self.documents, f)
        print("Index built and saved.")

    def load_index(self):
        if os.path.exists(VECTOR_DB_PATH) and os.path.exists(DOCS_PATH):
            self.index = faiss.read_index(VECTOR_DB_PATH)
            with open(DOCS_PATH, 'rb') as f:
                self.documents = pickle.load(f)
            return True
        return False

    def retrieve(self, query, k=3):
        if self.index is None:
            loaded = self.load_index()
            if not loaded:
                self.build_index()
        
        if self.model is None:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    'document': self.documents[idx],
                    'score': float(distances[0][i])
                })
        return results

if __name__ == "__main__":
    rag = MedicalRAG()
    rag.build_index()
    print(rag.retrieve("patient has chest pain"))
