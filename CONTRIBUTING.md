# Contributing to RAG FAQ Assistant

Thank you for considering contributing to this project! Here's how you can help:

## Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rag-faq-assistant.git
   cd rag-faq-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env  # Then edit .env with your settings
   ```

## Code Style

- Follow PEP 8 guidelines for Python code
- Include docstrings for all functions and classes
- Write unit tests for new functionality

## Project Structure

- `create_embeddings.py`: Creates and stores document embeddings
- `query_assistant.py`: Handles user queries and returns relevant information
- `document_scraper.py`: Example script to responsibly download documentation

## Adding New Features

When adding new features, please:

1. Discuss major changes in an issue first
2. Maintain backward compatibility where possible
3. Update documentation to reflect changes
4. Add tests that cover the new functionality

## Documentation

If you're updating documentation:

1. Keep the README updated with any user-facing changes
2. Use clear language and provide examples
3. Add diagrams or screenshots for complex concepts

## Testing

Run tests before submitting a pull request:

```bash
pytest
```

## Community

- Be respectful and inclusive
- Help others who have questions
- Follow the code of conduct

Thank you for contributing to making this project better!
