import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagnostic import Observation, ObservationSource, SafetyLevel
from app.gemini.schemas import GeminiTextExtraction, GeminiScreenshotExtraction, ExtractedSymptomItem
from app.gemini.client import GeminiAssistant

client = TestClient(app)


def test_gemini_structured_response_validation():
    """
    Tests Pydantic schema validation of Gemini structured outputs.
    """
    text_data = {
        "extracted_symptoms": [
            {"symptom_key": "high_cpu_usage", "value": True, "confidence": 0.95},
            {"symptom_key": "general_slowdown", "value": True, "confidence": 0.90}
        ]
    }
    parsed_text = GeminiTextExtraction.model_validate(text_data)
    assert len(parsed_text.extracted_symptoms) == 2
    assert parsed_text.extracted_symptoms[0].symptom_key == "high_cpu_usage"

    img_data = {
        "high_cpu_usage": True,
        "high_ram_usage": True,
        "high_disk_usage": False,
        "top_process_name": "chrome.exe",
        "extracted_symptoms": []
    }
    parsed_img = GeminiScreenshotExtraction.model_validate(img_data)
    assert parsed_img.high_cpu_usage is True
    assert parsed_img.top_process_name == "chrome.exe"


def test_invalid_gemini_output_rejection():
    """
    Verifies that malformed/invalid JSON structures raise ValidationErrors.
    """
    invalid_data = {"extracted_symptoms": "not_a_list"}
    with pytest.raises(Exception):
        GeminiTextExtraction.model_validate(invalid_data)


@patch("app.gemini.client.genai.Client")
def test_mocked_gemini_text_parsing_endpoint(mock_client_cls):
    """
    Tests POST /api/diagnostic/parse-text with mocked Gemini response.
    Tests must NOT call real Gemini API.
    """
    mock_response = MagicMock()
    mock_response.text = '{"extracted_symptoms": [{"symptom_key": "high_ram_usage", "value": true, "confidence": 0.95}]}'

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mock_client_cls.return_value = mock_client

    assistant = GeminiAssistant(api_key="mock_test_key")
    observations = assistant.parse_problem_text("My computer is running out of memory")

    assert len(observations) == 1
    assert observations[0].key == "high_ram_usage"
    assert observations[0].value is True
    assert observations[0].source == ObservationSource.USER_INPUT


@patch("app.gemini.client.genai.Client")
def test_mocked_gemini_screenshot_parsing_endpoint(mock_client_cls):
    """
    Tests POST /api/diagnostic/parse-screenshot with mocked Gemini response.
    """
    mock_response = MagicMock()
    mock_response.text = '{"high_cpu_usage": true, "high_ram_usage": false, "high_disk_usage": false, "top_process_name": "system_idle.exe", "extracted_symptoms": []}'

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mock_client_cls.return_value = mock_client

    assistant = GeminiAssistant(api_key="mock_test_key")
    observations = assistant.parse_task_manager_screenshot(b"fake_image_bytes")

    keys = [o.key for o in observations]
    assert "high_cpu_usage" in keys
    assert "top_process_name" in keys
    proc_obs = next(o for o in observations if o.key == "top_process_name")
    assert proc_obs.value == "system_idle.exe"
    assert proc_obs.source == ObservationSource.SCREENSHOT


def test_api_parse_text_endpoint():
    """
    Tests POST /api/diagnostic/parse-text via TestClient.
    """
    res = client.post("/api/diagnostic/parse-text", json={"text": "My PC is very lagging and high CPU usage"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(o["key"] in ["high_cpu_usage", "general_slowdown"] for o in data)


def test_api_parse_screenshot_endpoint():
    """
    Tests POST /api/diagnostic/parse-screenshot via TestClient.
    """
    res = client.post("/api/diagnostic/parse-screenshot", json={"screenshot_base64": "high_cpu_chrome"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_parsed_observations_reaching_expert_engine():
    """
    Verifies that parsed Gemini text and screenshot inputs successfully flow through
    POST /api/diagnostic/evaluate and reach the deterministic expert engine.
    """
    payload = {
        "domain": "performance",
        "text_input": "My PC is freezing and high RAM memory usage is observed",
        "screenshot_base64": "high_ram_chrome",
        "observations": []
    }
    res = client.post("/api/diagnostic/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "performance"
    assert len(data["processed_observations"]) > 0
    assert len(data["ranked_causes"]) > 0

    top_cause = data["ranked_causes"][0]
    assert top_cause["cause_id"] in ["cause_ram_exhaustion", "cause_app_hang", "cause_startup_overload"]
    assert len(top_cause["fix_steps"]) > 0
    for step in top_cause["fix_steps"]:
        assert step["safety_level"] in ["Safe", "Caution", "Advanced"]
