
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

from backend.ingestion.ingestion_manager import IngestionManager
from backend.ingestion.task_queue import IngestionTaskQueue
from backend.mcp.crew_manager import CrewManager

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in .env file")

# Initialize Supabase client (this will be mocked in tests)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# OAuth2 for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # In a real application, you would verify the token with Supabase
        # For now, we\"ll just return a dummy user if a token is present
        if token:
            return {"id": "dummy_user_id", "email": "dummy@example.com"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Initialize ChromaDB and Embeddings
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Initialize LLM (Ollama)
llm = Ollama(model="llama2") # Ensure Ollama is running and a model is pulled (e.g., ollama pull llama2)

# Initialize RAG QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectordb.as_retriever()
)

# Initialize Ingestion Manager and Task Queue
ingestion_manager = IngestionManager()
ingestion_queue = IngestionTaskQueue(ingestion_manager)

# Initialize CrewAI Manager
crew_manager = CrewManager()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    ingestion_queue.start_workers()

@app.on_event("shutdown")
async def shutdown_event():
    ingestion_queue.stop_workers()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/query_rag")
async def query_rag(query: dict, current_user: dict = Depends(get_current_user)):
    response = qa_chain.invoke({"query": query["query"]})
    return {"response": response["result"]}

@app.post("/run_mcp")
async def run_mcp(query: dict, current_user: dict = Depends(get_current_user)):
    response = crew_manager.run_crew(
        query=query["query"],
        agent_type=query["agent_type"],
        task_type=query["task_type"],
        **query.get("task_kwargs", {})
    )
    return {"response": response}

@app.post("/ingest_document")
async def ingest_document(file_path: str, file_type: str, current_user: dict = Depends(get_current_user)):
    # In a real application, you would handle file uploads securely
    # For now, we assume file_path is accessible by the ingestion manager
    ingestion_queue.add_task(file_path, file_type)
    return {"message": f"Ingestion task for {file_path} ({file_type}) added to queue."}


