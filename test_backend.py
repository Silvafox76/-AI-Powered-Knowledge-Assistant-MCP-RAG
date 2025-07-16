
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import os
import sys

# Add the project root to sys.path to allow importing backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock environment variables globally for all tests in this file
@pytest.fixture(scope="module", autouse=True)
def mock_env_and_supabase_setup_module():
    with patch.dict("os.environ", {
        "SUPABASE_URL": "http://mock-supabase.com",
        "SUPABASE_KEY": "mock-key"
    }):
        yield

@pytest.fixture(scope="function")
def client():
    from backend.main import app, get_current_user

    with patch("backend.main.create_client") as mock_create_client, \
         patch("backend.main.ingestion_queue") as mock_ingestion_queue:

        mock_supabase_client = MagicMock()
        mock_create_client.return_value = mock_supabase_client

        mock_ingestion_queue.start_workers = MagicMock()
        mock_ingestion_queue.stop_workers = MagicMock()

        app.dependency_overrides[get_current_user] = lambda: {"id": "test_user", "email": "test@example.com"}

        with TestClient(app) as c:
            yield c

        app.dependency_overrides = {}

@pytest.fixture(scope="function")
def client_no_auth():
    from backend.main import app, get_current_user
    original_dependency = app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        yield c
    if original_dependency:
        app.dependency_overrides[get_current_user] = original_dependency

def test_query_rag(client):
    with patch("backend.main.qa_chain") as mock_qa_chain:
        mock_qa_chain.invoke.return_value = {"result": "RAG response here"}

        response = client.post(
            "/query_rag",
            headers={
                "Authorization": "Bearer fake-jwt-token"
            },
            json={
                "query": "What is PRINCE2?"
            }
        )
        assert response.status_code == 200
        assert response.json() == {"response": "RAG response here"}
        mock_qa_chain.invoke.assert_called_once_with({"query": "What is PRINCE2?"})

def test_run_mcp(client):
    with patch("backend.main.crew_manager") as mock_crew_manager:
        mock_crew_manager.run_crew.return_value = "MCP crew output here"

        response = client.post(
            "/run_mcp",
            headers={
                "Authorization": "Bearer fake-jwt-token"
            },
            json={
                "query": "Explain the 7 principles of PRINCE2.",
                "agent_type": "prince2",
                "task_type": "prince2_analysis",
                "task_kwargs": {}
            }
        )
        assert response.status_code == 200
        assert response.json() == {"response": "MCP crew output here"}
        mock_crew_manager.run_crew.assert_called_once_with(
            query="Explain the 7 principles of PRINCE2.",
            agent_type="prince2",
            task_type="prince2_analysis",
            **{}
        )

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_current_user_valid_token(client):
    response = client.post(
        "/query_rag",
        headers={
            "Authorization": "Bearer valid-token"
        },
        json={
            "query": "test"
        }
    )
    assert response.status_code == 200

def test_get_current_user_no_token(client_no_auth):
    response = client_no_auth.post(
        "/query_rag",
        json={
            "query": "test"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


