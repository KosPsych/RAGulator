

# RAGulator


## Overview

RAGulator is a complete Retrieval-Augmented Generation (RAG) system developed for the ![AI Hackathon of AUEB Greece 2025](https://www.hackathongreece.ai/). The system specializes in processing complex legal PDF documents and can ingest information from:
- Scanned images
- Greek/English text
- Figures and tables

It provides accurate answers through a multilayered architecture with all components (DB, API, etc.) containerized with Docker for easy deployment.

## System Architecture

![Example Image](misc/overview.png)

The RAGulator system consists of several key components:

1. **Document Processing Pipeline**:
   - PDF parsing and text extraction
   - OCR for scanned documents 
   - Multilingual support (Greek/English)
   - Figure and table extraction

2. **Database Layer** (`graph_db`):
   - Knowledge graph storage
   - Vector embeddings for semantic search
   - Metadata indexing

3. **API Layer** (`api`):
   - RESTful endpoints for document processing
   - Query handling and response generation
   - Authentication and rate limiting

4. **User Interface** (`chat_ui`):
   - Intuitive chat interface
   - Document upload capabilities
   - Query history and management

5. **Miscellaneous Utilities** (`misc`):
   - Logging and monitoring
   - Testing frameworks
   - Helper scripts

## Installation

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- GPU acceleration (optional, but recommended for OCR and embedding generation)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/KosPsych/RAGulator.git
cd RAGulator

# Start all services
docker-compose up -d
```

The application will be available at `http://localhost:3000`.

## Usage

### Document Processing
```bash
# Upload a document via CLI
curl -X POST -F "file=@your_document.pdf" http://localhost:8000/api/documents

# Or use the web interface at http://localhost:3000
```

### Querying the System
```bash
# Example query via API
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What are the legal implications of Article 5?"}' \
  http://localhost:8000/api/query
```

## Development

### Project Structure
- `/api` - Backend API services
- `/chat_ui` - Frontend interface
- `/graph_db` - Database and vector store implementations
- `/misc` - Utility scripts and helpers

### Setting Up Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Features

- 🔍 **Precise Information Retrieval**: Advanced RAG system optimized for legal documents
- 🌍 **Multilingual Support**: Handles both Greek and English text
- 📊 **Rich Content Extraction**: Processes text, images, tables and figures
- 🔒 **Containerized Architecture**: Isolated components with Docker for security and scalability
- 💬 **Intuitive Interface**: User-friendly chat UI for querying documents

## Benchmarks

| Metric | Performance |
|--------|------------|
| Accuracy (retrieval) | 92.3% |
| Response Time | <2s |
| Document Processing Speed | ~3 MB/s |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AUEB Greece for hosting the AI Hackathon 2025
- All contributors and team members who made this project possible
  


