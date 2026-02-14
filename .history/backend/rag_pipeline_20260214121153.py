from sentence_transformers import SentenceTransformer
import chromadb

# multilingual embedding model
embedding_model = SentenceTransformer("BAAI/bge-m3")

# vector database
chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(
    name="medical_knowledge"
)

def add_document(text):

    embedding = embedding_model.encode(text).tolist()

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(hash(text))]
    )


def retrieve_context(query):

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )

    return results["documents"]
