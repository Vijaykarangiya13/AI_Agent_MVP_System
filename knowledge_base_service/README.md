# Knowledge Base Service

The Knowledge Base Service is responsible for storing, retrieving, and searching domain-specific knowledge using vector embeddings.

## Features

- Document ingestion and indexing
- Vector embedding generation using Google Gemini API
- Semantic search on stored knowledge
- Document retrieval based on relevance

## API Endpoints

### GET /

Returns basic information about the API.

### POST /ingest

Add a document to the knowledge base.

**Request Body:**
```json
{
  "content": "Document content to be stored",
  "metadata": {
    "title": "Optional document title",
    "source": "Optional source information",
    "author": "Optional author information"
  }
}
```

**Response:**
```json
{
  "message": "Document added successfully",
  "id": "document-id"
}
```

### POST /query

Query the knowledge base for relevant documents.

**Request Body:**
```json
{
  "query": "Your search query",
  "n_results": 3
}
```

**Response:**
```json
{
  "documents": [
    {
      "content": "Document content",
      "metadata": {
        "title": "Document title",
        "source": "Document source"
      }
    }
  ],
  "distances": [0.123, 0.456, 0.789]
}
```

### GET /documents

List all documents in the knowledge base.

**Response:**
```json
{
  "documents": [
    {
      "id": "document-id",
      "content": "Document content",
      "metadata": {
        "title": "Document title",
        "source": "Document source"
      }
    }
  ]
}
```

### POST /upload

Upload a document file to the knowledge base.

**Request Form:**
- `file`: The document file to upload
- `metadata`: JSON string with metadata (optional)

**Response:**
```json
{
  "message": "Document added successfully",
  "id": "document-id"
}
```

## Configuration

The service can be configured using environment variables:

- `GEMINI_API_KEY`: Google Gemini API key

## Running the Service

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app:app --reload --port 8001
```

### With Docker

```bash
docker build -t knowledge-base-service .
docker run -p 8001:8001 knowledge-base-service
```

### With Docker Compose

```bash
docker-compose up knowledge-base-service
```
