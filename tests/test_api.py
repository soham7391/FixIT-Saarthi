from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_parse_text_endpoint():
    response = client.post("/api/diagnostic/parse-text", json={"text_input": "My PC is very slow and freezing when Chrome is open"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_evaluate_diagnostic_workflow():
    response = client.post("/api/diagnostic/evaluate", json={
        "domain": "performance",
        "text_input": "My computer is lagging and high RAM memory usage is observed",
        "observations": [
            {
                "key": "app_freezing",
                "value": True,
                "confidence": 1.0,
                "source": "user_input"
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "performance"
    assert len(data["ranked_causes"]) > 0
    top_cause = data["ranked_causes"][0]
    assert top_cause["cause_id"] in ["cause_ram_exhaustion", "cause_startup_overload", "cause_app_hang"]
    assert len(top_cause["fix_steps"]) > 0
