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
            
        def is_summary_query(self, query):
            """Detect if the query is asking for a summary"""
            summary_keywords = ["summarize", "summarise", "summary", "overview", "highlight", 
                              "key points", "main points", "critical things", "important aspects"]
            query_lower = query.lower()
            return any(keyword in query_lower for keyword in summary_keywords)
            
        def format_regular_output(self, query, contexts, source_docs):
            """Format output for regular queries"""
            result = f"Top {len(contexts)} relevant passages for: {query}\n\n"
            for i, (text, score) in enumerate(contexts, 1):
                # Only include scores if they're meaningful
                if score < 0.95:  # Only show scores that indicate varying relevance
                    result += f"[{i}] (Relevance: {score:.2f}) {text}\n\n"
                else:
                    result += f"[{i}] {text}\n\n"
                    
            return result
            
        def format_summary_output(self, query, contexts, source_docs):
            """Format output for summary queries"""
            # Extract titles and main content from passages
            titles = []
            key_points = []
            
            for text, _ in contexts:
                # Try to extract a title if present
                lines = text.split('\n')
                if lines and lines[0].strip() and not lines[0].startswith('[Score:'):
                    title = lines[0].strip()
                    if len(title) < 100 and not title.startswith('http'):
                        titles.append(title)
                
                # Extract key sentences
                content = text.replace('\n', ' ')
                sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
                key_points.extend(sentences[:2])  # Take first two substantial sentences
            
            # Deduplicate titles and key points
            titles = list(dict.fromkeys(titles))
            key_points = list(dict.fromkeys(key_points))
            
            # Build summary output
            result = f"Summary of AWS Well-Architected Framework based on your query:\n\n"
            
            if titles:
                result += "Key Components:\n"
                for title in titles[:5]:  # Limit to 5 titles
                    result += f"- {title}\n"
                result += "\n"
            
            if key_points:
                result += "Key Points:\n"
                for i, point in enumerate(key_points[:10], 1):  # Limit to 10 key points
                    result += f"{i}. {point}.\n"
                    
            return result
        
        def __call__(self, query_dict):
            query = query_dict.get("query")
            # Get relevant documents
            results = self.vector_store.similarity_search_with_score(query, k=self.k)
            
            # Format contexts and gather metadata
            contexts = []
            source_docs = []
            for text, metadata, score in results:
                contexts.append((text, score))
                source_docs.append(metadata)
            
            # Check if this is a summary query
            if self.is_summary_query(query):
                # Increase number of results for summary queries
                if len(contexts) < 5:
                    more_results = self.vector_store.similarity_search_with_score(query, k=7)
                    for text, metadata, score in more_results:
                        if (text, score) not in contexts:
                            contexts.append((text, score))
                            source_docs.append(metadata)
                
                result = self.format_summary_output(query, contexts, source_docs)
            else:
                result = self.format_regular_output(query, contexts, source_docs)
            
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
    # Use more retrieved documents for summarization queries
    if any(word in question.lower() for word in ["summarize", "summarise", "summary", "overview"]):
        k = 7  # More documents for summaries
    else:
        k = 3  # Default for regular queries
        
    retriever = create_retriever(k=k)
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
