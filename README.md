# DeepResearch

A microservices-based research platform built as a learning project for
task decomposition, LangChain graphs, and vector embedding databases.

## Services

### Core Services

**database_service**
- Manages data persistence and database operations
- Provides REST API for CRUD operations on conversations, chat turns, invocations, profiles, and documents
- Uses PostgreSQL for relational data storage

**embedding_service** 
- Handles document embedding and semantic search
- Processes documents into chunks with metadata
- Uses Qdrant vector database for similarity search
- Implements sentence transformer models for text embeddings

**storage_service** 
- Manages file storage and retrieval
- Provides blob storage capabilities
- Integrates with database and embedding services for document processing

**graph_service** 
- Orchestrates AI-powered research workflows
- Supports configurable LLM providers via environment settings
- Coordinates between embedding and database services

**frontend_service** 
- Vue.js-based user interface
- Provides interactive access to research capabilities

### Infrastructure Services

**postgres**
- PostgreSQL database for structured data storage

**qdrant**
- Vector database for semantic search and embeddings

**minio**
- Object storage service for file management

## Prerequisites

- Docker and Docker Compose
- Claude API key
- Sentence transformer model specification

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# LLM provider configuration
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
DEFAULT_LLM_MODEL=claude  # Set to your preferred default model

# Embedding service
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2  # Optional; defaults to this value

# Database configuration
POSTGRES_USER=root
POSTGRES_PASSWORD=password
POSTGRES_DB=deepresearch

# MinIO configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Optional: File upload size limit
MAX_UPLOAD_SIZE_MB=50
```

## LLM Provider Configuration

Configure your API keys and model settings in `.env`:

1. Set your API key: `CLAUDE_API_KEY=your_claude_api_key`
2. Optionally set OpenAI values: `OPENAI_API_KEY` and `OPENAI_MODEL`
3. Set default model: `DEFAULT_LLM_MODEL=claude`

## Running the Project

Start all services:

```bash
docker-compose up
```

Start services in detached mode:

```bash
docker-compose up -d
```

Stop all services:

```bash
docker-compose down
```

Stop services and remove volumes:

```bash
docker-compose down -v
```

## Service URLs

- Frontend: http://localhost:8000
- Graph Service: http://localhost:8001
- Storage Service: http://localhost:8002
- Database Service: http://localhost:8003
- Embedding Service: http://localhost:8004
- PostgreSQL: localhost:5432
- Qdrant: http://localhost:6333
- MinIO Console: http://localhost:9001

## Health Checks

All services include health check endpoints at `/health` for monitoring service availability.
