import os
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBDy2EW8XxdELXOjM1Shos_8Gl_YnwzuRc")
client = genai.Client(api_key=GEMINI_API_KEY)

# Service URLs
KNOWLEDGE_BASE_URL = os.getenv("KNOWLEDGE_BASE_URL", "http://localhost:8001")
SEARCH_URL = os.getenv("SEARCH_URL", "http://127.0.0.1:8002")  # Using 127.0.0.1 instead of localhost
HISTORY_URL = os.getenv("HISTORY_URL", "http://localhost:8003")

# Initialize FastAPI app
app = FastAPI(
    title="Chat Service",
    description="Main orchestrator for the AI Agent MVP",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    chat_id: Optional[str] = None
    message: str
    use_knowledge_base: bool = True
    use_web_search: bool = True

class ChatResponse(BaseModel):
    chat_id: str
    response: str
    source: str
    context: Optional[List[Dict[str, Any]]] = None

class LectureRequest(BaseModel):
    topic: str
    context: Optional[str] = None

class LectureResponse(BaseModel):
    lecture: str
    topic: str

# Initialize the Gemini model
GEMINI_MODEL = "models/gemini-2.0-flash"  # Using the full model name from the available models

@app.get("/")
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "Chat Service API - AI Agent MVP",
        "endpoints": {
            "/chat": "Chat with the AI agent",
            "/generate-lecture": "Generate a lecture on a specific topic",
            "/models": "List available models"
        }
    }

@app.get("/models")
async def list_models():
    """List available models"""
    try:
        models = []
        for model in client.models.list():
            models.append({"name": model.name, "display_name": model.display_name})
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

async def query_knowledge_base(query: str) -> Optional[Dict[str, Any]]:
    """Query the knowledge base service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{KNOWLEDGE_BASE_URL}/query",
                json={"query": query, "n_results": 3}
            )

            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Error querying knowledge base: {str(e)}")
        return None

async def search_web(query: str) -> Optional[Dict[str, Any]]:
    """Search the web using the search service"""
    try:
        print(f"Searching the web for: {query}")
        print(f"Search URL: {SEARCH_URL}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{SEARCH_URL}/search",
                    json={"query": query, "max_results": 3}
                )

                print(f"Search response status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"Search results: {result}")
                    return result
                else:
                    print(f"Search failed with status code: {response.status_code}")
                    print(f"Response text: {response.text}")
                return None
            except Exception as e:
                print(f"Exception during search request: {str(e)}")
                return None
    except Exception as e:
        print(f"Error searching the web: {str(e)}")
        return None

async def get_chat_history(chat_id: str) -> Optional[Dict[str, Any]]:
    """Get chat history from the history service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{HISTORY_URL}/history/{chat_id}")

            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return None

async def create_chat_session() -> Optional[Dict[str, Any]]:
    """Create a new chat session in the history service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{HISTORY_URL}/history")

            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Error creating chat session: {str(e)}")
        return None

async def add_message_to_history(chat_id: str, role: str, content: str) -> Optional[Dict[str, Any]]:
    """Add a message to chat history in the history service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{HISTORY_URL}/history/{chat_id}/messages",
                json={"role": role, "content": content}
            )

            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Error adding message to history: {str(e)}")
        return None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI agent"""
    try:
        # Get or create chat session
        chat_id = request.chat_id
        history_available = True

        if not chat_id:
            try:
                chat_session = await create_chat_session()
                if chat_session:
                    chat_id = chat_session["chat_id"]
                else:
                    # Generate a temporary chat ID if history service is not available
                    import uuid
                    chat_id = str(uuid.uuid4())
                    history_available = False
            except Exception as e:
                print(f"Error creating chat session: {str(e)}")
                # Generate a temporary chat ID if history service is not available
                import uuid
                chat_id = str(uuid.uuid4())
                history_available = False

        # Add user message to history if history service is available
        if history_available:
            try:
                await add_message_to_history(chat_id, "user", request.message)
            except Exception as e:
                print(f"Error adding message to history: {str(e)}")
                history_available = False

        # Get chat history for context if history service is available
        history_context = ""
        if history_available:
            try:
                chat_history = await get_chat_history(chat_id)
                if chat_history and "messages" in chat_history:
                    # Format the last 5 messages for context
                    messages = chat_history["messages"][-5:]
                    for msg in messages:
                        history_context += f"{msg['role']}: {msg['content']}\n"
            except Exception as e:
                print(f"Error getting chat history: {str(e)}")
                history_available = False

        # Try knowledge base first if enabled
        knowledge_context = []
        source = "gemini"
        if request.use_knowledge_base:
            kb_results = await query_knowledge_base(request.message)
            if kb_results and "documents" in kb_results and kb_results["documents"]:
                source = "knowledge_base"
                for doc in kb_results["documents"]:
                    knowledge_context.append({
                        "content": doc["content"],
                        "metadata": doc["metadata"]
                    })

        # If no knowledge base results and web search is enabled, try web search
        web_results = []
        if not knowledge_context and request.use_web_search:
            print(f"No knowledge base results found, trying web search for: {request.message}")
            search_results = await search_web(request.message)
            print(f"Web search results: {search_results}")
            if search_results and "results" in search_results and search_results["results"]:
                source = "web_search"
                for result in search_results["results"]:
                    web_results.append({
                        "title": result["title"],
                        "body": result["body"],
                        "href": result["href"]
                    })
            else:
                print("No web search results found or invalid response format")

        # Prepare prompt for Gemini
        prompt = f"""You are an AI assistant. Answer the following question based on the provided context.

User question: {request.message}

"""

        if history_context:
            prompt += f"\nConversation history:\n{history_context}\n"

        if knowledge_context:
            prompt += "\nKnowledge base context:\n"
            for i, doc in enumerate(knowledge_context):
                prompt += f"Document {i+1}:\n{doc['content']}\n\n"

        if web_results:
            prompt += "\nWeb search results:\n"
            for i, result in enumerate(web_results):
                prompt += f"Result {i+1}: {result['title']}\n{result['body']}\n{result['href']}\n\n"

        prompt += "\nPlease provide a helpful, accurate, and concise response."

        # Generate response with Gemini
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        # Get the response text
        response_text = response.text

        # Add assistant response to history if history service is available
        if history_available:
            try:
                await add_message_to_history(chat_id, "assistant", response_text)
            except Exception as e:
                print(f"Error adding assistant response to history: {str(e)}")

        # Return the response
        context = []
        if knowledge_context:
            context = knowledge_context
        elif web_results:
            context = web_results

        return ChatResponse(
            chat_id=chat_id,
            response=response_text,
            source=source,
            context=context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.get("/chat/{chat_id}")
async def get_chat(chat_id: str):
    """Get chat history by ID"""
    try:
        chat_history = await get_chat_history(chat_id)
        if not chat_history:
            raise HTTPException(status_code=404, detail=f"Chat session with ID {chat_id} not found")

        return chat_history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat: {str(e)}")

def generate_lecture(topic: str, context: str = None):
    """Generate a lecture on a specific topic using Google Gemini API"""
    try:
        # Create the template
        template = f"""
        As an accomplished university professor and expert in {topic}, your task is to develop an elaborate, exhaustive, and highly detailed lecture on the subject.
        Remember to generate content ensuring both novice learners and advanced students can benefit from your expertise.

        Use the following context to inform your lecture:

        {context if context else "No specific context provided. Create a comprehensive lecture based on your knowledge."}

        Structure your lecture with:
        1. Introduction to {topic}
        2. Key concepts and principles
        3. Important theories and applications
        4. Recent developments and future directions
        5. Conclusion and key takeaways
        """

        # Generate the lecture using Gemini
        response = client.models.generate_content(
            model="models/gemini-2.0-flash",  # Using the same model as chat for consistency
            contents=template
        )

        # Get the response text
        lecture_text = response.text

        return lecture_text
    except Exception as e:
        print(f"Error generating lecture: {str(e)}")
        return f"Error generating lecture: {str(e)}"

@app.post("/generate-lecture", response_model=LectureResponse)
async def generate_lecture_endpoint(request: LectureRequest):
    """Generate a lecture on a specific topic using knowledge from the knowledge base"""
    try:
        # Get the topic
        topic = request.topic

        # Query the knowledge base for relevant information
        kb_results = await query_knowledge_base(topic)

        # Extract context from knowledge base results
        kb_context = ""
        if kb_results and "documents" in kb_results and kb_results["documents"]:
            for doc in kb_results["documents"]:
                kb_context += doc["content"] + "\n\n"

        # If no context was found in knowledge base, use the provided context
        context = kb_context if kb_context else request.context

        # Generate the lecture
        lecture = generate_lecture(topic, context)

        # Return the response
        return LectureResponse(
            lecture=lecture,
            topic=topic
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lecture: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
