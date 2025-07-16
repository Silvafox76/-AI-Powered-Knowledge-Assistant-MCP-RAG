"""
Simplified FastAPI application for testing the AI Knowledge Assistant.
This version mocks heavy dependencies for demonstration purposes.
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Knowledge Assistant",
    description="Production-ready AI-powered knowledge assistant with RAG and MCP capabilities",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    mode: str = "rag"
    agent_type: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    mode: str
    agent_used: Optional[str] = None
    sources: List[str] = []
    timestamp: datetime

class IngestionRequest(BaseModel):
    content: str
    content_type: str = "text/plain"
    metadata: Dict[str, Any] = {}

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

# Mock authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mock authentication for testing."""
    token = credentials.credentials
    if not token or token == "invalid":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Mock user for testing
    return User(
        id=1,
        username="admin",
        email="admin@example.com",
        full_name="System Administrator",
        is_active=True
    )

# Authentication endpoints
@app.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Mock login endpoint."""
    if login_data.username == "admin" and login_data.password == "admin123":
        return Token(
            access_token="mock-jwt-token-for-testing",
            token_type="bearer",
            expires_in=86400
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

@app.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )

# RAG query endpoint
@app.post("/query/rag", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Mock RAG query processing."""
    try:
        # Mock response based on query
        if "prince2" in request.query.lower():
            response = """Based on the knowledge base, here are the PRINCE2 principles:

1. Continued business justification
2. Learn from experience  
3. Defined roles and responsibilities
4. Manage by stages
5. Manage by exception
6. Focus on products
7. Tailor to suit the project environment

These principles form the foundation of the PRINCE2 methodology."""
            sources = ["PRINCE2 Managing Successful Projects (Chapter 3)", "PMBOK Guide 7th Edition"]
        else:
            response = f"This is a mock RAG response for the query: '{request.query}'. In a real implementation, this would search the vector database and generate a comprehensive answer based on your knowledge base."
            sources = ["Mock Document 1", "Mock Document 2"]
        
        return QueryResponse(
            response=response,
            mode="rag",
            sources=sources,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# MCP query endpoint
@app.post("/query/mcp", response_model=QueryResponse)
async def query_mcp(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Mock MCP agent query processing."""
    try:
        agent_type = request.agent_type or "general"
        
        response = f"This is a mock response from the {agent_type.upper()} agent for: '{request.query}'. The agent would provide specialized expertise in {agent_type} methodology and best practices."
        
        return QueryResponse(
            response=response,
            mode="mcp",
            agent_used=agent_type,
            sources=[f"{agent_type.upper()} Knowledge Base"],
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error processing MCP query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Document ingestion endpoint
@app.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Mock file ingestion."""
    try:
        content = await file.read()
        
        return {
            "message": f"File '{file.filename}' ingested successfully",
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "chunks_created": 5,  # Mock number
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error ingesting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting file: {str(e)}")

# Text ingestion endpoint
@app.post("/ingest/text")
async def ingest_text(
    request: IngestionRequest,
    current_user: User = Depends(get_current_user)
):
    """Mock text ingestion."""
    try:
        return {
            "message": "Text content ingested successfully",
            "content_length": len(request.content),
            "content_type": request.content_type,
            "chunks_created": 3,  # Mock number
            "metadata": request.metadata,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error ingesting text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting text: {str(e)}")

# Get available agents
@app.get("/agents")
async def get_available_agents(current_user: User = Depends(get_current_user)):
    """Mock agents list."""
    try:
        agents = [
            {"id": "prince2", "name": "PRINCE2", "description": "PRINCE2 project management specialist", "status": "active"},
            {"id": "agile", "name": "Agile", "description": "Agile and Scrum methodology expert", "status": "active"},
            {"id": "itil", "name": "ITIL", "description": "ITIL service management specialist", "status": "active"},
            {"id": "ai_strategy", "name": "AI Strategy", "description": "AI strategy and digital transformation expert", "status": "active"},
            {"id": "pmbok", "name": "PMBOK", "description": "Traditional project management (PMBOK) specialist", "status": "active"},
            {"id": "general", "name": "General PM", "description": "General project management advisor", "status": "active"}
        ]
        
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting agents: {str(e)}")

# Get knowledge base stats
@app.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    """Mock knowledge base statistics."""
    try:
        return {
            "total_documents": 89,
            "total_chunks": 1247,
            "active_agents": 6,
            "system_status": "healthy",
            "last_updated": datetime.now(),
            "storage_used": "2.3 GB",
            "queries_today": 42
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)

