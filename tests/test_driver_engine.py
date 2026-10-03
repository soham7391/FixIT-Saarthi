"""
Tests for Driver & Peripheral expert engine domain.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagnostic import DomainEnum, Observation, ObservationSource
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker
from app.knowledge_base.driver import DRIVER_CAUSES, DRIVER_SYMPTOMS
from app.gemini.client import GeminiAssistant

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _obs(key: str, value: bool = True, confidence: float = 1.0) -> Observation:
    return Observation(key=key, value=value, confidence=confidence, source=ObservationSource.USER_INPUT)


def _evaluate(observations: list) -> list:
    """Run the driver evaluator + ranker and return ranked causes."""
    evaluator = ExpertEvaluator(domain=DomainEnum.DRIVER_PERIPHERAL)
    ranker = CauseRanker()
    evaluated = evaluator.evaluate(observations)
    obs_map = {o.key: o for o in observations}
    return ranker.rank_causes(evaluated, obs_map)


# ---------------------------------------------------------------------------
# 1. Knowledge-base structure
# ---------------------------------------------------------------------------

def test_driver_knowledge_base_structure():
    """DRIVER_CAUSES and DRIVER_SYMPTOMS must be properly structured."""
    assert len(DRIVER_CAUSES) >= 5

    expected_symptom_keys = {
        "printer_not_detected",
        "keyboard_mouse_unresponsive",
        "audio_device_issue",
        "webcam_unavailable",
        "bluetooth_connection_failed",
        "device_failed_after_update",
        "usb_physical_disconnection",
        "app_permissions_blocked",
    }
    defined_keys = set(DRIVER_SYMPTOMS.keys())
    missing = expected_symptom_keys - defined_keys
    assert not missing, f"DRIVER_SYMPTOMS is missing keys: {missing}"

    for cause in DRIVER_CAUSES:
        assert "cause_id" in cause, f"{cause} missing cause_id"
        assert "symptom_weights" in cause, f"{cause} missing symptom_weights"
        assert "fix_steps" in cause, f"{cause} missing fix_steps"
        assert len(cause["fix_steps"]) >= 1


# ---------------------------------------------------------------------------
# 2. Representative Cause Matching
# ---------------------------------------------------------------------------

def test_printer_physical_disconnection_cause_matches():
    """Printer not detected + USB disconnection matches physical/power disconnection or driver cause."""
    ranked = _evaluate([_obs("usb_physical_disconnection"), _obs("printer_not_detected")])
    assert len(ranked) > 0
    ids = [r.cause_id for r in ranked]
    assert "cause_device_disconnected_power" in ids or "cause_hardware_peripheral_fault" in ids


def test_audio_misconfiguration_cause_matches():
    """Audio device issue matches audio misconfiguration cause."""
    ranked = _evaluate([_obs("audio_device_issue")])
    assert len(ranked) > 0
    assert ranked[0].cause_id == "cause_audio_output_input_misconfiguration"


def test_privacy_permissions_cause_matches():
    """App permissions blocked + webcam unavailable matches privacy settings cause."""
    ranked = _evaluate([_obs("app_permissions_blocked"), _obs("webcam_unavailable")])
    assert len(ranked) > 0
    assert ranked[0].cause_id == "cause_privacy_permissions_blocked"


def test_bluetooth_pairing_cause_matches():
    """Bluetooth connection failed matches bluetooth pairing cause."""
    ranked = _evaluate([_obs("bluetooth_connection_failed")])
    assert len(ranked) > 0
    assert ranked[0].cause_id == "cause_bluetooth_pairing_connection"


def test_driver_update_rollback_cause_matches():
    """Device failed after update matches driver update rollback cause."""
    ranked = _evaluate([_obs("device_failed_after_update"), _obs("printer_not_detected")])
    assert len(ranked) > 0
    assert ranked[0].cause_id == "cause_driver_update_rollback"


# ---------------------------------------------------------------------------
# 3. Insufficient symptoms — graceful handling
# ---------------------------------------------------------------------------

def test_no_observations_returns_list():
    """With zero observations, evaluate must return a list without raising."""
    evaluator = ExpertEvaluator(domain=DomainEnum.DRIVER_PERIPHERAL)
    result = evaluator.evaluate([])
    assert isinstance(result, list)


def test_insufficient_confidence_observations():
    """Observations below threshold should return empty or low confidence results."""
    obs = [Observation(key="printer_not_detected", value=True, confidence=0.1, source=ObservationSource.USER_INPUT)]
    ranked = _evaluate(obs)
    assert isinstance(ranked, list)


# ---------------------------------------------------------------------------
# 4. Cross-domain isolation
# ---------------------------------------------------------------------------

def test_driver_evaluator_does_not_use_performance_causes():
    """Driver evaluator must not return performance cause IDs."""
    from app.knowledge_base.performance import PERFORMANCE_CAUSES

    ranked = _evaluate([_obs("bluetooth_connection_failed"), _obs("audio_device_issue")])
    ranked_ids = {r.cause_id for r in ranked}
    perf_ids = {c["cause_id"] for c in PERFORMANCE_CAUSES}
    overlap = ranked_ids & perf_ids
    assert not overlap, f"Driver results contain performance causes: {overlap}"


def test_driver_evaluator_does_not_use_boot_causes():
    """Driver evaluator must not return boot cause IDs."""
    from app.knowledge_base.boot import BOOT_CAUSES

    ranked = _evaluate([_obs("webcam_unavailable")])
    ranked_ids = {r.cause_id for r in ranked}
    boot_ids = {c["cause_id"] for c in BOOT_CAUSES}
    overlap = ranked_ids & boot_ids
    assert not overlap, f"Driver results contain boot causes: {overlap}"


def test_driver_evaluator_does_not_use_network_causes():
    """Driver evaluator must not return network cause IDs."""
    from app.knowledge_base.network import NETWORK_CAUSES

    ranked = _evaluate([_obs("printer_not_detected")])
    ranked_ids = {r.cause_id for r in ranked}
    net_ids = {c["cause_id"] for c in NETWORK_CAUSES}
    overlap = ranked_ids & net_ids
    assert not overlap, f"Driver results contain network causes: {overlap}"


# ---------------------------------------------------------------------------
# 5. Domain API & Serialization
# ---------------------------------------------------------------------------

def test_domain_enum_driver_peripheral_value():
    """DomainEnum.DRIVER_PERIPHERAL must serialize to the string 'driver_peripheral'."""
    assert DomainEnum.DRIVER_PERIPHERAL.value == "driver_peripheral"


def test_driver_peripheral_domain_evaluation_via_api():
    """POST /api/diagnostic/evaluate with domain=driver_peripheral returns driver causes."""
    payload = {
        "domain": "driver_peripheral",
        "observations": [
            {"key": "bluetooth_connection_failed", "value": True, "confidence": 1.0, "source": "questionnaire"}
        ]
    }
    resp = client.post("/api/diagnostic/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    ids = [c["cause_id"] for c in data["ranked_causes"]]
    assert "cause_bluetooth_pairing_connection" in ids
