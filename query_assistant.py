"""
Query interface for the FAQ assistant using the FAISS vector store

LEGAL DISCLAIMER:
- This project is not affiliated with, endorsed by, or connected to Amazon Web Services.
- The answers provided are based on processed documentation and may not be current.
- Users should always refer to the official AWS documentation for authoritative information.
- AWS Well-Architected Framework documentation is copyrighted by AWS.

Citation:
Amazon Web Services, "AWS Well-Architected Framework", AWS Documentation
https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
"""
import os
import sys
import pickle
from pathlib import Path
from dotenv import load_dotenv

# Import our custom vector store
from create_embeddings import SimpleVectorStore, TfidfEmbeddings

# Load environment variables from .env file
load_dotenv()

# Check for OpenAI API key (only needed for the LLM, not for embeddings)
if "OPENAI_API_KEY" not in os.environ:
    print("Error: OPENAI_API_KEY not found in .env file or environment variables")
    print("Note: API key still required for ChatOpenAI model but not for embeddings")
    exit(1)

# Path to the vector store
VECTOR_STORE_PATH = Path("./faiss_index")

# We'll use a simpler approach without the langchain retriever abstraction

def load_vector_store():
    """Load the vector store"""
    if not VECTOR_STORE_PATH.exists():
        print(f"Vector store not found at {VECTOR_STORE_PATH}")
        print("Please run create_embeddings.py first")
        sys.exit(1)
    
    print("Loading vector store...")
    try:
        return SimpleVectorStore.load(VECTOR_STORE_PATH)
    except Exception as e:
        print(f"Error loading vector store: {e}")
        print("Make sure you've created the vector store using create_embeddings.py")
        exit(1)

def create_retriever(k=5):
    """Create a retriever for the FAQ assistant"""
    vector_store = load_vector_store()
    
    # Wrap everything in a simple callable object
    class SimpleRetriever:
        def __init__(self, vector_store, k=5):
            self.vector_store = vector_store
            self.k = k
            
        def __call__(self, query_dict):
            query = query_dict.get("query")
            # Get relevant documents
            results = self.vector_store.similarity_search_with_score(query, k=self.k)
            # Format contexts and gather metadata
            contexts = []
            source_docs = []
            for text, metadata, score in results:
                contexts.append(f"[Score: {score:.4f}] {text}")
                source_docs.append(metadata)
            
            # Combine and return the contexts as the result
            result = f"Top {len(contexts)} relevant passages for: {query}\n\n" + \
                    "\n\n---\n\n".join(contexts)
            
            # Return in expected format
            return {"result": result, "source_documents": source_docs}
    
    return SimpleRetriever(vector_store, k)

def interactive_qa():
    """Interactive question-answering"""
    print("\n=== AWS Well-Architected Framework FAQ Assistant (Retrieval Only Mode) ===")
    print("Ask any question about AWS Well-Architected Framework (type 'exit' to quit)")
    print("\nDISCLAIMER: This tool is not affiliated with AWS. Answers are for reference only.")
    print("Always refer to official AWS documentation for authoritative information.")
    print("AWS Well-Architected Framework documentation is copyrighted by AWS.\n")
    
    retriever = create_retriever(k=3)
    
    while True:
        query = input("\nYour question: ")
        if query.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
            
        if not query.strip():
            continue
            
        try:
            result = retriever({"query": query})
            print("\n" + result["result"])
            
            # Display sources
            print("\nSources:")
            for i, doc in enumerate(result["source_documents"]):
                print(f"  {i+1}. {doc['source']}")
        except Exception as e:
            print(f"Error: {e}")

def answer_question(question):
    """Answer a single question programmatically"""
    retriever = create_retriever(k=3)
    result = retriever({"query": question})
    return {
        "answer": result["result"],
        "sources": [doc['source'] for doc in result["source_documents"]]
    }

if __name__ == "__main__":
    # Print disclaimer for command-line use
    print("\nDISCLAIMER: This tool is not affiliated with or endorsed by AWS.")
    print("For authoritative information, refer to the official AWS documentation.")
    
    # If a question is passed as an argument, answer it once
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"\nQuery: {question}")
        result = answer_question(question)
        print(result["answer"])
        print("\nSources:")
        for i, source in enumerate(result["sources"]):
            print(f"  {i+1}. {source}")
    else:
        # Otherwise, start interactive mode
        interactive_qa()
