"""
Create embeddings for document chunks and store them in a FAISS vector database
AWS Well-Architected Framework FAQ Assistant - Embedding Creation Script

This script creates TF-IDF embeddings for AWS Well-Architected Framework documentation
and stores them in a FAISS vector index for efficient similarity search.

LEGAL DISCLAIMER:
- This project is not affiliated with, endorsed by, or connected to Amazon Web Services.
- Users must ensure they have the legal right to use any AWS documentation.
- This script processes documentation that users have downloaded themselves.
- AWS Well-Architected Framework documentation is copyrighted by AWS.
- Users should always refer to the official AWS documentation for authoritative information.

Citation:
Amazon Web Services, "AWS Well-Architected Framework", AWS Documentation
https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
"""
import json
from pathlib import Path
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# No API key needed for local embeddings

# Paths
CHUNK_DIR = Path("./chunks")
VECTOR_STORE_PATH = "./faiss_index"

class TfidfEmbeddings:
    """Simple TF-IDF based embeddings"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self.trained = False
        self.vectors = None
    
    def fit(self, texts):
        """Fit the vectorizer on the texts"""
        self.vectors = self.vectorizer.fit_transform(texts)
        self.trained = True
    
    def embed_documents(self, texts):
        """Embed documents using the fitted vectorizer"""
        if not self.trained:
            raise ValueError("Vectorizer not trained. Call fit() first.")
        return self.vectorizer.transform(texts).toarray()
    
    def embed_query(self, text):
        """Embed a single query"""
        if not self.trained:
            raise ValueError("Vectorizer not trained. Call fit() first.")
        return self.vectorizer.transform([text]).toarray()[0]

class SimpleVectorStore:
    """Simple vector store using FAISS"""
    
    def __init__(self, embeddings, texts=None, metadatas=None):
        self.embeddings = embeddings
        self.texts = texts or []
        self.metadatas = metadatas or []
        self.index = None
    
    def add_texts(self, texts, metadatas=None):
        """Add texts to the vector store"""
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)
        
        if not self.embeddings.trained:
            self.embeddings.fit(self.texts)
        
        vectors = self.embeddings.embed_documents(texts)
        
        if self.index is None:
            # Initialize FAISS index
            dimension = vectors.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        # Add vectors to index
        self.index.add(np.array(vectors).astype('float32'))
    
    def similarity_search_with_score(self, query, k=5):
        """Search for similar documents"""
        query_vector = self.embeddings.embed_query(query)
        
        # Search in FAISS
        distances, indices = self.index.search(
            np.array([query_vector]).astype('float32'), k
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts):
                results.append((self.texts[idx], self.metadatas[idx], distances[0][i]))
        
        return results
        
    def save(self, path):
        """Save the vector store to disk"""
        data = {
            "texts": self.texts,
            "metadatas": self.metadatas,
        }
        
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Save texts and metadata
        with open(f"{path}/data.pickle", "wb") as f:
            pickle.dump(data, f)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}/index.faiss")
        
        # Save vectorizer
        with open(f"{path}/vectorizer.pickle", "wb") as f:
            pickle.dump(self.embeddings.vectorizer, f)
    
    @classmethod
    def load(cls, path):
        """Load the vector store from disk"""
        # Load texts and metadata
        with open(f"{path}/data.pickle", "rb") as f:
            data = pickle.load(f)
        
        # Load vectorizer
        with open(f"{path}/vectorizer.pickle", "rb") as f:
            vectorizer = pickle.load(f)
        
        # Create embeddings
        embeddings = TfidfEmbeddings()
        embeddings.vectorizer = vectorizer
        embeddings.trained = True
        
        # Create vector store
        store = cls(embeddings, data["texts"], data["metadatas"])
        
        # Load FAISS index
        store.index = faiss.read_index(f"{path}/index.faiss")
        
        return store

def main():
    """Create embeddings and save to FAISS vector store"""
    print("Loading document chunks and their metadata...")
    
    # Load metadata
    with open(CHUNK_DIR / "metadata.json", "r") as f:
        metadata_list = json.load(f)
    
    # Prepare texts and metadata
    texts = []
    metadatas = []
    
    print(f"Processing {len(metadata_list)} document chunks...")
    for item in tqdm(metadata_list):
        chunk_path = CHUNK_DIR / f"{item['id']}.txt"
        if chunk_path.exists():
            chunk_text = chunk_path.read_text(encoding="utf-8")
            texts.append(chunk_text)
            metadatas.append(item)
        else:
            print(f"Warning: Chunk file not found: {chunk_path}")
    
    print(f"Creating TF-IDF embeddings for {len(texts)} chunks...")
    embeddings = TfidfEmbeddings()
    vector_store = SimpleVectorStore(embeddings)
    vector_store.add_texts(texts, metadatas)
    
    # Save the index
    print(f"Saving vector store to {VECTOR_STORE_PATH}")
    vector_store.save(VECTOR_STORE_PATH)
    print("Embeddings and vector store created successfully!")

if __name__ == "__main__":
    main()
