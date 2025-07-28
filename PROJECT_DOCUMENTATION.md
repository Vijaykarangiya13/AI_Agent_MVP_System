# AI Agent MVP with Google Gemini - Project Documentation

## Project Overview

This project implements a microservices-based AI assistant that can chat with users, answer questions using a knowledge base, fall back to web search when needed, and maintain conversation history. The system uses Google's Gemini API for natural language processing and generation.

## System Architecture

The system consists of four microservices that work together to provide a complete AI agent experience:

```
[Chat Service (Port 8000)]  
 ↓  
[Knowledge Base Service (Port 8001)] [Search Service (Port 8002)] [History Service (Port 8003)]
```

### Components and Data Flow

1. **User Interaction**: Users interact with the Chat Service by sending messages.
2. **Knowledge Base Query**: The Chat Service first checks if the query can be answered using the Knowledge Base Service.
3. **Web Search Fallback**: If no relevant information is found in the knowledge base, the Chat Service falls back to the Search Service.
4. **History Management**: All interactions are stored in the History Service to maintain context for future conversations.
5. **Response Generation**: The Chat Service uses Google Gemini API to generate natural language responses based on the context from the knowledge base or web search.

## Microservices Details

### 1. Chat Service (Orchestrator)

The Chat Service is the main entry point for user interactions and coordinates between all other services.

**Key Features:**
- Processes user queries and determines the best source for answers
- Integrates with Google Gemini API for natural language generation
- Provides endpoints for chatting and generating lecture content
- Maintains conversation history through the History Service
- Falls back to web search when knowledge base has no answer

**Implementation Details:**
- Built with FastAPI for high-performance API endpoints
- Uses Google Gemini API for natural language generation
- Implements a fallback mechanism from knowledge base to web search
- Handles error cases when other services are unavailable

**API Endpoints:**
- `GET /`: Root endpoint with API information
- `GET /models`: List available Gemini models
- `POST /chat`: Submit user query and receive response
- `POST /generate-lecture`: Generate a lecture on a specific topic

### 2. Knowledge Base Service

The Knowledge Base Service stores and retrieves domain-specific knowledge.

**Key Features:**
- Ingests and indexes documents (including PDFs)
- Converts queries to embeddings for semantic search
- Performs semantic search on stored knowledge
- Returns relevant document chunks for context

**Implementation Details:**
- Uses Google Gemini API for embeddings
- Stores documents and their embeddings
- Implements semantic search functionality
- Supports document uploads including PDFs

**API Endpoints:**
- `GET /`: Root endpoint with API information
- `POST /query`: Search knowledge base with embedded query
- `POST /ingest`: Add documents to knowledge base
- `GET /documents`: List all documents in the knowledge base
- `DELETE /documents/{document_id}`: Remove a document from the knowledge base

### 3. Search Service

The Search Service provides web search capabilities when the knowledge base can't answer a query.

**Key Features:**
- Queries the web using DuckDuckGo
- Extracts and cleans relevant information
- Returns formatted search results

**Implementation Details:**
- Uses DuckDuckGo for web searches
- Formats search results for easy consumption by the Chat Service
- Implements error handling for failed searches

**API Endpoints:**
- `GET /`: Root endpoint with API information
- `POST /search`: Perform web search with the given query

### 4. History Service

The History Service maintains conversation context across interactions.

**Key Features:**
- Creates and manages unique chat sessions
- Stores message history by chat ID
- Retrieves conversation context

**Implementation Details:**
- Uses MongoDB with in-memory fallback
- Implements CRUD operations for chat sessions and messages
- Provides endpoints for managing conversation history

**API Endpoints:**
- `GET /`: Root endpoint with API information
- `POST /sessions`: Create a new chat session
- `GET /sessions/{chat_id}`: Get a specific chat session
- `POST /sessions/{chat_id}/messages`: Add a message to a chat session
- `GET /sessions/{chat_id}/messages`: Get all messages in a chat session

## Technical Implementation

### Technologies Used

- **Backend Framework**: FastAPI
- **AI Model**: Google Gemini API
- **Database**: MongoDB (with in-memory fallback)
- **Vector Store**: ChromaDB (for embeddings and retrieval)
- **Search**: DuckDuckGo API
- **Documentation**: Swagger UI (available at `/docs` endpoint for each service)

### Key Features Implemented

1. **Conversational AI**
   - Natural language processing and generation using Google Gemini API
   - Context-aware responses based on conversation history
   - Structured prompt templates for consistent responses

2. **Knowledge Base**
   - Document ingestion and indexing
   - Semantic search using embeddings
   - Relevant context extraction for AI responses

3. **Web Search**
   - Integration with DuckDuckGo for web searches
   - Extraction of relevant information from search results
   - Fallback mechanism when knowledge base doesn't have answers

4. **Conversation History**
   - Unique chat sessions for different conversations
   - Message history storage and retrieval
   - Context maintenance across multiple interactions

5. **Lecture Generation**
   - Structured content generation on specific topics
   - Context-aware educational content
   - Formatting for readability

## Challenges and Solutions

### Challenge 1: Google Gemini API Integration
**Problem**: The Google Gemini API client interface changed, causing errors with the `generative_model` method.
**Solution**: Updated the code to use the correct `models.generate_content` method and fixed the model name format.

### Challenge 2: Service Communication
**Problem**: Services needed to communicate with each other while handling failures gracefully.
**Solution**: Implemented robust error handling and fallback mechanisms in the Chat Service to handle cases when other services are unavailable.

### Challenge 3: Knowledge Base Search
**Problem**: Needed an efficient way to search through documents and find relevant information.
**Solution**: Implemented semantic search using embeddings to find contextually relevant information rather than just keyword matching.

### Challenge 4: History Service Reliability
**Problem**: The History Service needed to be reliable even when the database is unavailable.
**Solution**: Implemented an in-memory fallback for the History Service when MongoDB is not available.

## Future Improvements

1. **Enhanced Web Search**
   - Implement more sophisticated web search capabilities with multiple sources
   - Add caching for frequently searched queries

2. **Knowledge Base Improvements**
   - Add support for more document types
   - Implement document chunking strategies for better context retrieval
   - Add automatic knowledge base updates from trusted sources

3. **User Experience**
   - Develop a simple web UI for easier interaction
   - Add user authentication and personalization

4. **Performance Optimizations**
   - Implement caching for improved response times
   - Optimize embedding generation and storage

5. **Deployment**
   - Add Kubernetes configuration for scalable deployment
   - Implement monitoring and logging for production use

## Conclusion

The AI Agent MVP successfully implements a microservices architecture for an AI assistant that can chat with users, answer questions using a knowledge base, fall back to web search when needed, and maintain conversation history. The system demonstrates the power of combining different services to create a comprehensive AI solution.

The modular architecture allows for easy extension and improvement of individual components without affecting the entire system. The use of Google's Gemini API provides powerful natural language processing capabilities, while the knowledge base and web search features ensure that the AI agent can provide accurate and relevant information to users.
