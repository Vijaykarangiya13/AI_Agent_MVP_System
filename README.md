# AI Agent MVP

A microservices-based AI assistant that can chat with users, answer questions using a knowledge base, fall back to web search when needed, and maintain conversation history. Built with FastAPI and Google's Gemini API.

## System Architecture

```
[Chat Service]
 ↓
[Knowledge Base Service] [Search Service] [History Service]
```

## Microservices

### 1. Chat Service (Orchestrator)
- **Purpose**: Main entry point that manages user interactions and coordinates between services
- **Features**:
  - Receive user queries via API endpoint
  - Determine if query can be answered from knowledge base
  - Fall back to search when knowledge base has no answer
  - Store conversation history
  - Format and return responses to users
- **Tech**: FastAPI, Google Gemini API

### 2. Knowledge Base Service
- **Purpose**: Store, retrieve and search domain-specific knowledge
- **Features**:
  - Ingest and index documents
  - Convert queries to embeddings
  - Perform semantic search on stored knowledge
  - Return relevant document chunks
- **Tech**: ChromaDB, Vector Embeddings

### 3. Search Service
- **Purpose**: Provide web search capabilities when knowledge base can't answer
- **Features**:
  - Query web using DuckDuckGo
  - Extract and clean relevant information
  - Return formatted search results
- **Tech**: DuckDuckGo Search API

### 4. History Service
- **Purpose**: Maintain conversation context across interactions
- **Features**:
  - Create and manage unique chat sessions
  - Store message history by chat ID
  - Retrieve conversation context
- **Tech**: MongoDB (with in-memory fallback)

## API Endpoints

### Chat Service
- **POST /chat**: Submit user query and receive response
- **GET /chat/{chat_id}**: Retrieve chat history

### Knowledge Base Service
- **POST /ingest**: Add documents to knowledge base
- **POST /query**: Search knowledge base with embedded query
- **GET /documents**: List all documents in the knowledge base
- **POST /upload**: Upload a document file to the knowledge base

### Search Service
- **POST /search**: Perform web search

### History Service
- **POST /history**: Create a new chat session
- **GET /history/{chat_id}**: Retrieve chat history
- **POST /history/{chat_id}/messages**: Add a message to chat history

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn
- Google GenAI SDK
- ChromaDB
- MongoDB (optional, falls back to in-memory storage)
- DuckDuckGo Search API

## Setup and Installation

### Prerequisites
- Docker and Docker Compose (optional)
- Python 3.9+
- Google Gemini API key (already configured in the code)

### Running with Docker Compose

1. Start all services:
```bash
docker-compose up
```

2. Access the services:
- Chat Service: http://localhost:8000
- Knowledge Base Service: http://localhost:8001
- Search Service: http://localhost:8002
- History Service: http://localhost:8003

### Running Locally

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Unix/MacOS:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies for each service:
```bash
cd chat_service && pip install -r requirements.txt
cd ../knowledge_base_service && pip install -r requirements.txt
cd ../search_service && pip install -r requirements.txt
cd ../history_service && pip install -r requirements.txt
```

4. Start each service in a separate terminal:
```bash
# Terminal 1
cd chat_service && uvicorn app:app --reload --port 8000

# Terminal 2
cd knowledge_base_service && uvicorn app:app --reload --port 8001

# Terminal 3
cd search_service && uvicorn app:app --reload --port 8002

# Terminal 4
cd history_service && uvicorn app:app --reload --port 8003
```

### Using the API

#### Chat with the AI Agent
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is artificial intelligence?", "use_knowledge_base": true, "use_web_search": true}'
```

#### Generate a Lecture
```bash
curl -X POST http://localhost:8000/generate-lecture \
  -H "Content-Type: application/json" \
  -d '{"topic": "Artificial Intelligence"}'
```

#### Add Document to Knowledge Base
```bash
curl -X POST http://localhost:8001/ingest \
  -F "file=@/path/to/document.pdf" \
  -F "metadata={\"title\": \"Document Title\"}"
```

#### Search the Web
```bash
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "latest news about AI"}'
```

#### Create a Chat Session
```bash
curl -X POST http://localhost:8003/sessions \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Documentation

Once the services are running, you can access the interactive API documentation at:

- Chat Service: `http://localhost:8000/docs`
- Knowledge Base Service: `http://localhost:8001/docs`
- Search Service: `http://localhost:8002/docs`
- History Service: `http://localhost:8003/docs`

For detailed project documentation, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md).

## Troubleshooting

### Common Issues

1. **Services not connecting**
   - Make sure all services are running on the correct ports
   - Check that the service URLs in the Chat Service are correctly configured
   - Verify network connectivity between services

2. **API key errors**
   - Verify your Google Gemini API key is correctly set in the `.env` file
   - Check for any API usage limits or restrictions

3. **MongoDB connection issues**
   - If using MongoDB, check your connection string
   - The system will fall back to in-memory storage if MongoDB is not available

4. **Document ingestion problems**
   - Ensure documents are in supported formats (PDF, TXT)
   - Check file permissions and paths

### Logs

Each service logs information to the console. Check these logs for error messages if you encounter issues:

```bash
# Example of checking logs for the Chat Service
cd chat_service && uvicorn app:app --reload --port 8000 --log-level debug
```
## Author
Vijay Karangiya — [GitHub](https://github.com/Vijaykarangiya13)

## License

MIT
