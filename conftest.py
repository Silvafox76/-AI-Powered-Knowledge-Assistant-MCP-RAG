
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Ollama and RetrievalQA before importing any modules that use them
# This ensures the mocks are in place when the modules are loaded.

# Mock Ollama class directly
# This mock will be returned when Ollama() is called.
mock_ollama_class = MagicMock()
mock_ollama_instance = MagicMock()
mock_ollama_instance.invoke.return_value = "Mocked LLM response"
mock_ollama_class.return_value = mock_ollama_instance

patch("langchain_community.llms.ollama.Ollama", mock_ollama_class).start()

# Mock RetrievalQA.from_chain_type
mock_qa_chain_instance = MagicMock()
mock_qa_chain_instance.invoke.return_value = {"result": "Mocked RAG response"}
patch("langchain.chains.RetrievalQA.from_chain_type", MagicMock(return_value=mock_qa_chain_instance)).start()

# Now, import the app and get_current_user after patching
from backend.main import app, get_current_user

@pytest.fixture(scope="function", autouse=True)
def mock_env_and_supabase_setup(monkeypatch):
    # Patch create_client and ingestion_queue
    monkeypatch.setattr("backend.main.create_client", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr("backend.main.ingestion_queue", MagicMock())
    monkeypatch.setattr("backend.main.ingestion_queue.start_workers", MagicMock())
    monkeypatch.setattr("backend.main.ingestion_queue.stop_workers", MagicMock())

    # Mock environment variables
    monkeypatch.setenv("SUPABASE_URL", "http://mock-supabase.com")
    monkeypatch.setenv("SUPABASE_KEY", "mock-key")

    yield

@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_current_user] = lambda: {"id": "test_user", "email": "test@example.com"}
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}

@pytest.fixture(scope="session")
def client_no_auth():
    original_dependency = app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        yield c
    if original_dependency:
        app.dependency_overrides[get_current_user] = original_dependency


