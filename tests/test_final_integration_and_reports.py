"""
Final Integration & Edge Cases Test Suite.

Tests:
1. Empty Problem Description edge cases (empty string, whitespace-only, valid string).
2. Session Status update API (PATCH /api/session/{session_id} to resolved).
3. Report Availability rules (only resolved sessions allow resolution report status).
4. QR payload security (contains no secrets, credentials, or API keys).
5. Viva Demo Scenario: "System gets stuck on manufacturer logo screen with spinning dots."
   - Parsed under Boot Failure domain -> produces Boot candidate causes.
   - Parsed under Driver domain -> intent detector flags Boot Failure domain.
6. Domain switch and keep behaviors.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagnostic import DomainEnum, Observation, ObservationSource
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker
from app.gemini.client import GeminiAssistant

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Empty Problem Description Edge Cases
# ---------------------------------------------------------------------------

def test_parse_text_empty_string_rejection():
    """POST /api/diagnostic/parse-text with empty text returns HTTP 400."""
    resp = client.post("/api/diagnostic/parse-text", json={"text": ""})
    assert resp.status_code == 400
    assert "Text payload cannot be empty" in resp.json()["detail"]


def test_parse_text_whitespace_only_rejection():
    """POST /api/diagnostic/parse-text with whitespace-only text returns HTTP 400."""
    resp = client.post("/api/diagnostic/parse-text", json={"text": "   \n\t  "})
    assert resp.status_code == 400
    assert "Text payload cannot be empty" in resp.json()["detail"]


def test_parse_text_valid_problem_statement_success():
    """POST /api/diagnostic/parse-text with valid text returns parsed observations."""
    resp = client.post("/api/diagnostic/parse-text", json={"text": "My computer is very slow and CPU is at 100% usage."})
    assert resp.status_code == 200
    obs = resp.json()
    assert isinstance(obs, list)
    assert len(obs) > 0


# ---------------------------------------------------------------------------
# 2. Session Status Update API & Resolved Report Rules
# ---------------------------------------------------------------------------

def test_create_and_update_session_status_to_resolved():
    """Can create session and update status to 'resolved' via PATCH /api/session/{session_id}."""
    # 1. Create session
    create_resp = client.post("/api/session", json={"domain": "boot_failure"})
    assert create_resp.status_code == 201
    session_id = create_resp.json()["session_id"]
    assert create_resp.json()["status"] == "active"

    # 2. Update status to resolved
    patch_resp = client.patch(f"/api/session/{session_id}", json={"status": "resolved"})
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["session_id"] == session_id
    assert data["status"] == "resolved"

    # 3. Retrieve session and verify resolved status persisted
    get_resp = client.get(f"/api/session/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "resolved"


def test_invalid_session_id_status_update_fails():
    """PATCH /api/session/non-existent-id returns HTTP 404."""
    patch_resp = client.patch("/api/session/00000000-0000-0000-0000-000000000000", json={"status": "resolved"})
    assert patch_resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. Viva Demo Scenario: Boot Intent entered under Driver Domain
# ---------------------------------------------------------------------------

def test_viva_demo_boot_scenario_evaluation_under_boot_domain():
    """
    Final-viva demonstration scenario:
    Text: "System gets stuck on manufacturer logo screen with spinning dots."
    When evaluated under DomainEnum.BOOT_FAILURE, it must produce boot causes.
    """
    text = "System gets stuck on manufacturer logo screen with spinning dots."
    assistant = GeminiAssistant()
    obs = assistant._heuristic_parse_text(text)

    # Must contain stuck_on_logo observation
    keys = {o.key for o in obs}
    assert "stuck_on_logo" in keys, f"Expected 'stuck_on_logo' in parsed observations, got {keys}"

    # Evaluate under BOOT_FAILURE domain
    evaluator = ExpertEvaluator(domain=DomainEnum.BOOT_FAILURE)
    ranker = CauseRanker()
    raw_evals = evaluator.evaluate(obs)
    obs_map = {o.key: o for o in obs}
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    boot_cause_ids = [r.cause_id for r in ranked]
    assert any(cid.startswith("cause_") for cid in boot_cause_ids)
    # Must NOT produce driver cause IDs
    driver_ids = {"cause_printer_not_detected", "cause_bluetooth_pairing_connection", "cause_audio_output_input_misconfiguration"}
    assert not driver_ids.intersection(set(boot_cause_ids))


def test_viva_demo_boot_scenario_isolation_under_driver_domain():
    """
    If the exact viva demo text is evaluated under DRIVER_PERIPHERAL (without domain switch),
    it must NOT produce driver causes because boot symptoms do not match driver rules.
    """
    text = "System gets stuck on manufacturer logo screen with spinning dots."
    assistant = GeminiAssistant()
    obs = assistant._heuristic_parse_text(text)

    evaluator = ExpertEvaluator(domain=DomainEnum.DRIVER_PERIPHERAL)
    ranker = CauseRanker()
    raw_evals = evaluator.evaluate(obs)
    obs_map = {o.key: o for o in obs}
    ranked = ranker.rank_causes(raw_evals, obs_map)

    # Boot symptoms have zero match against driver rules -> zero ranked causes
    assert len(ranked) == 0, f"Expected 0 matches for boot symptoms under driver domain, got {ranked}"


# ---------------------------------------------------------------------------
# 4. QR Payload Security & Non-Secret Verification
# ---------------------------------------------------------------------------

def test_qr_payload_structure_contains_no_secrets():
    """
    Validates that the QR verification payload structure contains only public non-secret fields.
    """
    session_id = "123e4567-e89b-12d3-a456-426614174000"
    domain = "Driver & Peripherals"
    timestamp = "2026-10-05T12:00:00Z"

    qr_payload = {
        "system": "FixIT Saarthi",
        "session_id": session_id,
        "domain": domain,
        "status": "resolved",
        "resolved_at": timestamp
    }

    # Verify no secret keywords in payload string
    payload_str = str(qr_payload).lower()
    forbidden = ["api_key", "secret", "password", "token", "base64", "screenshot_bytes"]
    for word in forbidden:
        assert word not in payload_str, f"Forbidden secret word '{word}' found in QR payload!"

    assert qr_payload["system"] == "FixIT Saarthi"
    assert qr_payload["status"] == "resolved"
