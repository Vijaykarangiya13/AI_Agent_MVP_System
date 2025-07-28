import os
import uuid
import json
import numpy as np
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import PyPDF2
import io

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "put your api key")
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Base Service",
    description="A service for storing and retrieving knowledge base documents",
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

# Simple in-memory document store
DOCUMENTS = []
DOCUMENT_PATH = "./data/documents.json"

# Load existing documents if available
try:
    if os.path.exists(DOCUMENT_PATH):
        with open(DOCUMENT_PATH, 'r') as f:
            DOCUMENTS = json.load(f)
        print(f"Loaded {len(DOCUMENTS)} documents from {DOCUMENT_PATH}")
except Exception as e:
    print(f"Error loading documents: {str(e)}")
    DOCUMENTS = []

# Models
class Document(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}
    embedding: Optional[List[float]] = None

class DocumentInput(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class QueryRequest(BaseModel):
    query: str
    n_results: int = 3

class QueryResponse(BaseModel):
    documents: List[Document]
    distances: List[float]

# Helper function to generate embeddings using Gemini
def generate_embedding(text: str):
    """Generate embeddings for text using Gemini API"""
    try:
        embedding_model = client.get_model("embedding-001")
        result = embedding_model.embed_content(
            content=text,
            task_type="retrieval_document"
        )
        return result.embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Fallback to a simple embedding if Gemini fails
        return [0.0] * 768

# Helper function to compute cosine similarity
def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors"""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)

# Helper function to save documents to disk
def save_documents():
    """Save documents to disk"""
    os.makedirs(os.path.dirname(DOCUMENT_PATH), exist_ok=True)
    with open(DOCUMENT_PATH, 'w') as f:
        json.dump(DOCUMENTS, f)

@app.get("/")
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "Knowledge Base Service API",
        "endpoints": {
            "/ingest": "Add documents to the knowledge base",
            "/query": "Query the knowledge base",
            "/documents": "List all documents in the knowledge base",
            "/upload": "Upload a document file to the knowledge base",
            "/upload-pdf": "Upload a PDF file to the knowledge base"
        }
    }

@app.post("/ingest")
async def ingest_document(document: DocumentInput):
    """Add a document to the knowledge base"""
    try:
        # Generate a unique ID for the document
        doc_id = str(uuid.uuid4())

        # Generate embedding for the document
        embedding = generate_embedding(document.content)

        # Create a new document
        new_doc = Document(
            id=doc_id,
            content=document.content,
            metadata=document.metadata,
            embedding=embedding
        )

        # Add the document to the in-memory store
        DOCUMENTS.append(new_doc.dict())

        # Save documents to disk
        save_documents()

        return {"message": "Document added successfully", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """Query the knowledge base for relevant documents"""
    try:
        if not DOCUMENTS:
            return QueryResponse(documents=[], distances=[])

        # Generate embedding for the query
        query_embedding = generate_embedding(request.query)

        # Compute similarities
        similarities = []
        for doc in DOCUMENTS:
            if doc.get("embedding"):
                similarity = cosine_similarity(query_embedding, doc["embedding"])
                similarities.append((doc, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top N results
        top_n = min(request.n_results, len(similarities))
        results = similarities[:top_n]

        # Format the response
        documents = []
        distances = []
        for doc, similarity in results:
            documents.append(Document(**doc))
            distances.append(1.0 - similarity)  # Convert similarity to distance

        return QueryResponse(
            documents=documents,
            distances=distances
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all documents in the knowledge base"""
    try:
        return {"documents": DOCUMENTS}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form("{}")
):
    """Upload a document file to the knowledge base"""
    try:
        # Read the file content
        content = await file.read()
        content_text = content.decode("utf-8")

        # Create document with metadata
        document = DocumentInput(
            content=content_text,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                **eval(metadata)  # Convert string to dict (careful with security!)
            }
        )

        # Ingest the document
        result = await ingest_document(document)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    metadata: str = Form("{}")
):
    """Upload a PDF file to the knowledge base"""
    try:
        # Check if file is a PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Read the file content
        content = await file.read()

        # Parse PDF content
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text_content = ""

        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text() + "\n\n"

        # Create document with metadata
        document = DocumentInput(
            content=text_content,
            metadata={
                "filename": file.filename,
                "content_type": "application/pdf",
                "page_count": len(pdf_reader.pages),
                **eval(metadata)  # Convert string to dict (careful with security!)
            }
        )

        # Ingest the document
        result = await ingest_document(document)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
