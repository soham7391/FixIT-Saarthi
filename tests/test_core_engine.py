import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.diagnostic import (
    Observation,
    ObservationSource,
    SafetyLevel,
    DiagnosticRequest,
    DomainEnum
)
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker

client = TestClient(app)


def test_high_cpu_scenario():
    """
    Scenario: High CPU Bottleneck / Rogue Process.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="high_cpu_usage", value=92.0, confidence=1.0),
        Observation(key="general_slowdown", value=True, confidence=1.0),
        Observation(key="top_process_name", value="system_idle.exe", confidence=1.0)
    ]
    obs_map = {o.key: o for o in observations}

    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    top_cause = ranked[0]
    assert top_cause.cause_id == "cause_cpu_bottleneck"
    assert top_cause.confidence_score >= 0.70
    assert "high_cpu_usage" in top_cause.matched_symptoms
    assert any(step.safety_level in [SafetyLevel.SAFE, SafetyLevel.CAUTION, SafetyLevel.ADVANCED] for step in top_cause.fix_steps)


def test_high_ram_scenario():
    """
    Scenario: High RAM Exhaustion / Memory Leak.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="high_ram_usage", value=95.0, confidence=1.0),
        Observation(key="app_freezing", value=True, confidence=1.0),
        Observation(key="top_process_name", value="chrome.exe", confidence=1.0)
    ]
    obs_map = {o.key: o for o in observations}

    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    top_cause = ranked[0]
    assert top_cause.cause_id == "cause_ram_exhaustion"
    assert top_cause.confidence_score >= 0.70
    assert "high_ram_usage" in top_cause.matched_symptoms


def test_high_disk_scenario():
    """
    Scenario: Disk I/O Saturation / HDD Bottleneck.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="high_disk_usage", value=True, confidence=1.0),
        Observation(key="general_slowdown", value=True, confidence=1.0)
    ]
    obs_map = {o.key: o for o in observations}

    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    top_cause = ranked[0]
    assert top_cause.cause_id == "cause_disk_saturation"
    assert top_cause.confidence_score >= 0.70
    assert "high_disk_usage" in top_cause.matched_symptoms


def test_mixed_freezing_scenario():
    """
    Scenario: Freezing and general system slowdown with multiple symptoms.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="general_slowdown", value=True, confidence=1.0),
        Observation(key="app_freezing", value=True, confidence=1.0),
        Observation(key="high_ram_usage", value=True, confidence=1.0)
    ]
    obs_map = {o.key: o for o in observations}

    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    top_cause_ids = [c.cause_id for c in ranked]
    assert "cause_ram_exhaustion" in top_cause_ids or "cause_startup_overload" in top_cause_ids


def test_schema_validations():
    obs = Observation(key="high_cpu_usage", value=True, confidence=0.9)
    assert obs.key == "high_cpu_usage"
    assert obs.confidence == 0.9

    req = DiagnosticRequest(domain=DomainEnum.PERFORMANCE, observations=[obs])
    assert req.domain == DomainEnum.PERFORMANCE
    assert len(req.observations) == 1


def test_health_api():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_evaluate_api():
    payload = {
        "domain": "performance",
        "observations": [
            {"key": "high_cpu_usage", "value": 90.0, "confidence": 1.0},
            {"key": "general_slowdown", "value": True, "confidence": 1.0}
        ],
        "top_process_name": "system_idle.exe"
    }
    res = client.post("/api/diagnostic/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "performance"
    assert data["status"] == "completed"
    assert len(data["ranked_causes"]) > 0
    top_cause = data["ranked_causes"][0]
    assert top_cause["cause_id"] == "cause_cpu_bottleneck"
    assert len(top_cause["fix_steps"]) > 0
    for step in top_cause["fix_steps"]:
        assert step["safety_level"] in ["Safe", "Caution", "Advanced"]
