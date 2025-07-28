# History Service

The History Service maintains conversation context across interactions by storing and retrieving chat history.

## Features

- Create and manage unique chat sessions
- Store message history by chat ID
- Retrieve conversation context
- MongoDB integration with in-memory fallback

## API Endpoints

### GET /

Returns basic information about the API.

### POST /history

Create a new chat session.

**Response:**
```json
{
  "chat_id": "new-chat-session-id",
  "messages": [],
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:00"
}
```

### GET /history/{chat_id}

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

### POST /history/{chat_id}/messages

Add a message to chat history.

**Request Body:**
```json
{
  "role": "user|assistant",
  "content": "Message content"
}
```

**Response:**
```json
{
  "chat_id": "chat-session-id",
  "messages": [
    {
      "role": "user",
      "content": "Previous user message",
      "timestamp": "2023-01-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "Previous assistant response",
      "timestamp": "2023-01-01T12:00:05"
    },
    {
      "role": "user",
      "content": "New user message",
      "timestamp": "2023-01-01T12:01:00"
    }
  ],
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:01:00"
}
```

## Configuration

The service can be configured using environment variables:

- `MONGO_URI`: MongoDB connection URI
- `DB_NAME`: MongoDB database name
- `COLLECTION_NAME`: MongoDB collection name for chat history

## Running the Service

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app:app --reload --port 8003
```

### With Docker

```bash
docker build -t history-service .
docker run -p 8003:8003 history-service
```

### With Docker Compose

```bash
docker-compose up history-service
```
