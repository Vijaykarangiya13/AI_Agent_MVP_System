import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "ai_agent_mvp")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chat_history")

# Initialize FastAPI app
app = FastAPI(
    title="History Service",
    description="A service for storing and retrieving chat history",
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

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"Connected to MongoDB: {MONGO_URI}")
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")
    # Create a fallback in-memory storage
    chat_history_store = {}

# Models
class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatSession(BaseModel):
    chat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AddMessageRequest(BaseModel):
    chat_id: Optional[str] = None
    role: str
    content: str

@app.get("/")
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "History Service API",
        "endpoints": {
            "/history": "Create a new chat session",
            "/history/{chat_id}": "Get chat history by ID",
            "/history/{chat_id}/messages": "Add a message to chat history"
        }
    }

@app.post("/history", response_model=ChatSession)
async def create_chat_session():
    """Create a new chat session"""
    try:
        # Create a new chat session
        chat_session = ChatSession()
        
        # Store in MongoDB if available
        try:
            collection.insert_one(chat_session.dict())
        except Exception as e:
            print(f"Error storing in MongoDB: {str(e)}")
            # Fallback to in-memory storage
            chat_history_store[chat_session.chat_id] = chat_session.dict()
        
        return chat_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat session: {str(e)}")

@app.get("/history/{chat_id}", response_model=ChatSession)
async def get_chat_history(chat_id: str):
    """Get chat history by ID"""
    try:
        # Try to get from MongoDB
        try:
            result = collection.find_one({"chat_id": chat_id})
            if result:
                return ChatSession(**result)
        except Exception as e:
            print(f"Error retrieving from MongoDB: {str(e)}")
            # Fallback to in-memory storage
            if chat_id in chat_history_store:
                return ChatSession(**chat_history_store[chat_id])
        
        # If not found in either storage
        raise HTTPException(status_code=404, detail=f"Chat session with ID {chat_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

@app.post("/history/{chat_id}/messages", response_model=ChatSession)
async def add_message(chat_id: str, message: AddMessageRequest):
    """Add a message to chat history"""
    try:
        # Get the current chat session
        try:
            chat_session_data = collection.find_one({"chat_id": chat_id})
            if not chat_session_data:
                # Try in-memory storage
                if chat_id in chat_history_store:
                    chat_session_data = chat_history_store[chat_id]
                else:
                    # If not found, create a new session with the provided ID
                    chat_session = ChatSession(chat_id=chat_id)
                    chat_session_data = chat_session.dict()
        except Exception as e:
            print(f"Error retrieving from MongoDB: {str(e)}")
            # Fallback to in-memory storage or create new
            if chat_id in chat_history_store:
                chat_session_data = chat_history_store[chat_id]
            else:
                chat_session = ChatSession(chat_id=chat_id)
                chat_session_data = chat_session.dict()
        
        # Create a chat session object
        chat_session = ChatSession(**chat_session_data)
        
        # Add the new message
        new_message = Message(
            role=message.role,
            content=message.content
        )
        chat_session.messages.append(new_message)
        chat_session.updated_at = datetime.now()
        
        # Update the storage
        try:
            collection.update_one(
                {"chat_id": chat_id},
                {"$set": chat_session.dict()},
                upsert=True
            )
        except Exception as e:
            print(f"Error updating MongoDB: {str(e)}")
            # Fallback to in-memory storage
            chat_history_store[chat_id] = chat_session.dict()
        
        return chat_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8003, reload=True)
