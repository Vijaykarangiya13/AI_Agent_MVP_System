# Chat Service

The Chat Service is the main orchestrator for the AI Agent MVP. It coordinates between the Knowledge Base Service, Search Service, and History Service to provide a comprehensive AI assistant experience.

## Features

- Processes user queries and generates responses using Google Gemini API
- Coordinates with Knowledge Base Service to retrieve relevant information
- Falls back to Search Service when knowledge base doesn't have an answer
- Maintains conversation context using History Service
- Provides a clean API for chat interactions

## API Endpoints

### GET /

Returns basic information about the API.

### POST /chat

Chat with the AI agent.

**Request Body:**
```json
{
  "chat_id": "optional-existing-chat-id",
  "message": "Your question or message",
  "use_knowledge_base": true,
  "use_web_search": true
}
```

**Response:**
```json
{
  "chat_id": "chat-session-id",
  "response": "AI response to your message",
  "source": "knowledge_base|web_search|gemini",
  "context": [
    {
      "content": "Relevant document content",
      "metadata": {}
    }
  ]
}
```

### GET /chat/{chat_id}

Get chat history by ID.

**Response:**
```json
{
  "chat_id": "chat-session-id",
  "messages": [
    {
      "role": "user",
      "content": "User message",
      "timestamp": "2023-01-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "Assistant response",
      "timestamp": "2023-01-01T12:00:05"
    }
  ],
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:05"
}
```

## Configuration

The service can be configured using environment variables:

- `GEMINI_API_KEY`: Google Gemini API key
- `KNOWLEDGE_BASE_URL`: URL of the Knowledge Base Service
- `SEARCH_URL`: URL of the Search Service
- `HISTORY_URL`: URL of the History Service

## Running the Service

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app:app --reload
```

### With Docker

```bash
docker build -t chat-service .
docker run -p 8000:8000 chat-service
```

### With Docker Compose

```bash
docker-compose up chat-service
```
