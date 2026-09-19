import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagnostic import DomainEnum, Observation, RankedCause, SafetyLevel, FixStep
from app.db.supabase import SupabaseSessionManager

client = TestClient(app)


def test_supabase_session_manager_in_memory_fallback():
    """
    Tests session manager CRUD operations with fallback/mocked store.
    """
    manager = SupabaseSessionManager()

    # 1. Create session
    session = manager.create_session(domain=DomainEnum.PERFORMANCE)
    assert session.session_id is not None
    assert session.domain == DomainEnum.PERFORMANCE
    assert session.status == "active"
    assert session.observations == []

    session_id = session.session_id

    # 2. Get session
    fetched = manager.get_session(session_id)
    assert fetched is not None
    assert fetched.session_id == session_id

    # 3. Update session
    obs = [Observation(key="high_ram_usage", value=True)]
    causes = [
        RankedCause(
            cause_id="cause_ram_exhaustion",
            cause_name="RAM Exhaustion",
            confidence_score=0.9,
            matched_symptoms=["high_ram_usage"],
            reasoning="High RAM detected",
            fix_steps=[
                FixStep(
                    step_number=1,
                    title="Close apps",
                    instruction="Close background tabs",
                    safety_level=SafetyLevel.SAFE,
                    verification_question="Did memory drop?"
                )
            ]
        )
    ]

    updated = manager.update_session(session_id, observations=obs, ranked_causes=causes, status="in_progress")
    assert updated is not None
    assert updated.status == "in_progress"
    assert len(updated.observations) == 1
    assert len(updated.ranked_causes) == 1
    assert updated.ranked_causes[0].cause_id == "cause_ram_exhaustion"


@patch("app.db.supabase.create_client")
def test_mocked_supabase_client_crud(mock_create_client):
    """
    Tests session CRUD operations using a mocked Supabase Client instance.
    Verifies tests do NOT depend on real Supabase credentials or network.
    """
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table

    mock_insert_res = MagicMock()
    mock_insert_res.data = [{
        "session_id": "test-uuid-1234",
        "domain": "performance",
        "observations": [],
        "ranked_causes": [],
        "status": "active",
        "created_at": "2026-09-18T12:00:00Z",
        "updated_at": "2026-09-18T12:00:00Z"
    }]
    mock_table.insert.return_value.execute.return_value = mock_insert_res

    mock_select_res = MagicMock()
    mock_select_res.data = [{
        "session_id": "test-uuid-1234",
        "domain": "performance",
        "observations": [{"key": "high_cpu_usage", "value": True, "confidence": 1.0, "source": "user_input"}],
        "ranked_causes": [],
        "status": "in_progress",
        "created_at": "2026-09-18T12:00:00Z",
        "updated_at": "2026-09-18T12:05:00Z"
    }]
    mock_table.select.return_value.eq.return_value.execute.return_value = mock_select_res

    manager = SupabaseSessionManager(url="https://mock.supabase.co", secret_key="mock_secret_key")
    manager.client = mock_supabase

    # Create
    created = manager.create_session(domain=DomainEnum.PERFORMANCE)
    assert created.session_id == "test-uuid-1234"

    # Fetch
    fetched = manager.get_session("test-uuid-1234")
    assert fetched is not None
    assert fetched.session_id == "test-uuid-1234"
    assert len(fetched.observations) == 1
    assert fetched.observations[0].key == "high_cpu_usage"


def test_session_api_create_and_get():
    """
    Tests POST /api/session and GET /api/session/{session_id} endpoints.
    """
    # Create
    create_res = client.post("/api/session", json={"domain": "performance"})
    assert create_res.status_code == 201
    data = create_res.json()
    assert "session_id" in data
    assert data["status"] == "active"

    session_id = data["session_id"]

    # Get
    get_res = client.get(f"/api/session/{session_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["session_id"] == session_id
    assert get_data["domain"] == "performance"


def test_session_api_missing_handling():
    """
    Tests GET /api/session/{session_id} with missing/non-existent session ID.
    Expects 404 Not Found error response.
    """
    res = client.get("/api/session/non-existent-session-id-999")
    assert res.status_code == 404
    err_data = res.json()
    assert "detail" in err_data
    assert "not found" in err_data["detail"].lower()


def test_diagnostic_persistence_integration():
    """
    Tests POST /api/diagnostic/evaluate with session_id.
    Verifies observations and ranked causes are persisted to the session.
    """
    # 1. Create active session
    create_res = client.post("/api/session", json={"domain": "performance"})
    session_id = create_res.json()["session_id"]

    # 2. Evaluate diagnostic with session_id
    eval_payload = {
        "session_id": session_id,
        "domain": "performance",
        "text_input": "My PC is lagging and high RAM memory usage is observed",
        "observations": [
            {"key": "app_freezing", "value": True, "confidence": 1.0, "source": "user_input"}
        ]
    }
    eval_res = client.post("/api/diagnostic/evaluate", json=eval_payload)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["session_id"] == session_id
    assert len(eval_data["ranked_causes"]) > 0

    # 3. Retrieve session and verify persisted results
    session_res = client.get(f"/api/session/{session_id}")
    assert session_res.status_code == 200
    session_data = session_res.json()
    assert session_data["status"] == "in_progress"
    assert len(session_data["observations"]) > 0
    assert len(session_data["ranked_causes"]) > 0


def test_diagnostic_missing_session_evaluation():
    """
    Tests POST /api/diagnostic/evaluate with invalid session_id.
    Expects 404 Not Found response.
    """
    eval_payload = {
        "session_id": "invalid-session-id-12345",
        "domain": "performance",
        "observations": [{"key": "high_cpu_usage", "value": True}]
    }
    res = client.post("/api/diagnostic/evaluate", json=eval_payload)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
