"""
Tests for the TF-IDF embedding and vector store functionality
"""
import sys
import os
import unittest
from pathlib import Path
import numpy as np
import tempfile
import pickle

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from create_embeddings import TfidfEmbeddings, SimpleVectorStore

class TestTfidfEmbeddings(unittest.TestCase):
    """Test the TfidfEmbeddings class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_texts = [
            "The AWS Well-Architected Framework helps you build secure applications",
            "AWS provides reliability as a key pillar in the framework",
            "Cost optimization helps you avoid unnecessary costs",
            "Performance efficiency is about using resources efficiently",
            "Operational excellence is about running and monitoring systems"
        ]
        self.embeddings = TfidfEmbeddings()
        self.embeddings.fit(self.sample_texts)
    
    def test_embedding_shape(self):
        """Test that embeddings have the expected shape"""
        vectors = self.embeddings.embed_documents(self.sample_texts)
        self.assertEqual(len(vectors), len(self.sample_texts))
        
        # All vectors should have the same dimensionality
        first_dim = vectors[0].shape[0]
        for vec in vectors:
            self.assertEqual(vec.shape[0], first_dim)
    
    def test_query_embedding(self):
        """Test embedding a query"""
        query = "What is AWS Well-Architected?"
        query_vector = self.embeddings.embed_query(query)
        
        # Query embedding should be a 1D array with same dimensionality as documents
        self.assertEqual(len(query_vector.shape), 1)
        doc_vectors = self.embeddings.embed_documents([self.sample_texts[0]])
        self.assertEqual(query_vector.shape[0], doc_vectors[0].shape[0])


class TestSimpleVectorStore(unittest.TestCase):
    """Test the SimpleVectorStore class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_texts = [
            "The AWS Well-Architected Framework helps you build secure applications",
            "AWS provides reliability as a key pillar in the framework",
            "Cost optimization helps you avoid unnecessary costs",
            "Performance efficiency is about using resources efficiently",
            "Operational excellence is about running and monitoring systems"
        ]
        self.sample_metadata = [
            {"source": "doc1.txt", "page": 1},
            {"source": "doc1.txt", "page": 2},
            {"source": "doc2.txt", "page": 1},
            {"source": "doc3.txt", "page": 1},
            {"source": "doc4.txt", "page": 1}
        ]
        self.embeddings = TfidfEmbeddings()
        self.embeddings.fit(self.sample_texts)
        self.vector_store = SimpleVectorStore(self.embeddings, self.sample_texts, self.sample_metadata)
        
    def test_similarity_search(self):
        """Test similarity search returns correct results"""
        query = "What is the AWS reliability pillar?"
        results = self.vector_store.similarity_search_with_score(query, k=2)
        
        # Should return 2 results
        self.assertEqual(len(results), 2)
        
        # Each result should be (document, score) tuple
        for doc, score in results:
            self.assertTrue(hasattr(doc, 'page_content'))
            self.assertTrue(hasattr(doc, 'metadata'))
            self.assertTrue(isinstance(score, float))
            
        # The most similar document should be the one about reliability
        self.assertIn("reliability", results[0][0].page_content.lower())
    
    def test_save_and_load(self):
        """Test saving and loading the vector store"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            save_path = Path(tmpdirname) / "test_vector_store"
            
            # Save the vector store
            self.vector_store.save(save_path)
            
            # Check that files were created
            self.assertTrue((save_path / "index.faiss").exists())
            self.assertTrue((save_path / "vectorizer.pkl").exists())
            self.assertTrue((save_path / "texts.pkl").exists())
            self.assertTrue((save_path / "metadatas.pkl").exists())
            
            # Load the vector store
            loaded_store = SimpleVectorStore.load(save_path)
            
            # Test that it works the same
            query = "What is the AWS reliability pillar?"
            original_results = self.vector_store.similarity_search_with_score(query, k=1)
            loaded_results = loaded_store.similarity_search_with_score(query, k=1)
            
            # Compare results (should be the same document)
            self.assertEqual(
                original_results[0][0].page_content,
                loaded_results[0][0].page_content
            )


if __name__ == '__main__':
    unittest.main()
