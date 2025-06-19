"""
Web interface for the RAG FAQ Assistant using Flask

This provides a simple web API and interface for interacting with the
FAQ assistant without using the command line.

LEGAL DISCLAIMER:
- This project is not affiliated with, endorsed by, or connected to AWS.
- The answers provided are based on processed documentation and may not be current.
- Users should always refer to the official AWS documentation for authoritative information.
- AWS Well-Architected Framework documentation is copyrighted by AWS.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try importing the query assistant, but provide fallback if it fails
try:
    from query_assistant import answer_question, create_retriever
    logger.info("Successfully imported query_assistant module")
    QUERY_ASSISTANT_AVAILABLE = True
except Exception as e:
    logger.error(f"Failed to import query_assistant module: {e}")
    logger.error("Will use mock functions instead")
    QUERY_ASSISTANT_AVAILABLE = False
    
    # Mock functions for testing
    def answer_question(question):
        return {
            "answer": f"This is a mock answer for: {question}",
            "sources": ["Mock source 1", "Mock source 2"]
        }
    
    def create_retriever():
        return None

app = Flask(__name__)

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Create a simple HTML template if it doesn't exist
index_html = templates_dir / "index.html"
if not index_html.exists():
    with open(index_html, "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>RAG FAQ Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .query-form {
            margin-bottom: 20px;
        }
        .query-input {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            margin-bottom: 10px;
        }
        .submit-button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        .answer {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .sources {
            margin-top: 20px;
            font-size: 14px;
        }
        .source-item {
            margin-bottom: 5px;
        }
        .disclaimer {
            font-size: 12px;
            color: #666;
            margin-top: 40px;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>RAG FAQ Assistant</h1>
        <p>Ask questions about your documentation</p>
    </div>
    
    <div class="query-form">
        <form id="questionForm">
            <input type="text" id="question" name="question" placeholder="Ask a question..." class="query-input" required>
            <button type="submit" class="submit-button">Ask</button>
        </form>
    </div>
    
    <div id="loading" class="loading">
        <p>Processing your question...</p>
    </div>
    
    <div id="answer-container" class="answer" style="display: none;">
        <h2>Answer:</h2>
        <div id="answer-text"></div>
        
        <div class="sources">
            <h3>Sources:</h3>
            <ul id="sources-list"></ul>
        </div>
    </div>
    
    <div class="disclaimer">
        <p><strong>Disclaimer:</strong> This tool is not affiliated with or endorsed by any documentation provider. 
        Always refer to the official documentation for authoritative information.</p>
    </div>
    
    <script>
        document.getElementById('questionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const question = document.getElementById('question').value;
            
            // Show loading state
            document.getElementById('loading').style.display = "block";
            document.getElementById('answer-container').style.display = "none";
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question }),
                });
                
                const data = await response.json();
                
                // Hide loading state
                document.getElementById('loading').style.display = "none";
                document.getElementById('answer-container').style.display = "block";
                
                // Display the answer
                document.getElementById('answer-text').innerText = data.answer;
                
                // Display sources
                const sourcesList = document.getElementById('sources-list');
                sourcesList.innerHTML = "";
                data.sources.forEach((source, index) => {
                    const li = document.createElement('li');
                    li.className = "source-item";
                    li.innerText = source;
                    sourcesList.appendChild(li);
                });
            } catch (error) {
                // Hide loading state
                document.getElementById('loading').style.display = "none";
                document.getElementById('answer-container').style.display = "block";
                document.getElementById('answer-text').innerText = "Error: " + error.message;
            }
        });
    </script>
</body>
</html>
        """)

@app.route('/', methods=['GET'])
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """Process a query and return the answer with sources"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400
            
        question = data['question']
        logger.info(f"Processing query: {question}")
        
        result = answer_question(question)
        logger.info("Query processed successfully")
        
        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"]
        })
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            "answer": f"Error processing your query: {e}",
            "sources": ["Error occurred"]
        }), 500

if __name__ == "__main__":
    # Get port from environment variable or default to 5001
    port = int(os.environ.get("PORT", 5001))
    
    # Print startup message
    print(f"\n{'=' * 60}")
    print(f"RAG FAQ Assistant Web Interface")
    print(f"{'=' * 60}")
    print(f"Access the web interface at http://localhost:{port}")
    print("Press Ctrl+C to exit")
    print(f"{'=' * 60}\n")
    
    # Print disclaimer
    print("DISCLAIMER: This tool is not affiliated with or endorsed by AWS.")
    print("For authoritative information, refer to the official AWS documentation.\n")
    
    # Start the server
    app.run(host="0.0.0.0", port=port, debug=True)
