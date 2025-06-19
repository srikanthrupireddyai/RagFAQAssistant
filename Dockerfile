FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p raw_docs
RUN mkdir -p vector_store
RUN mkdir -p templates

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VECTOR_STORE_PATH=vector_store
ENV DOCUMENT_CHUNKS_PATH=document_chunks.pkl

# Expose the port for the web interface
EXPOSE 5001

# Default command - web interface
CMD ["python", "flask_web_app.py"]

# Documentation about expected volumes
# Users should mount:
# - ./raw_docs:/app/raw_docs - For documentation files
# - ./vector_store:/app/vector_store - For persisting the vector store
# - ./templates:/app/templates - For custom UI templates (optional)
