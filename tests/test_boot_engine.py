import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagnostic import DomainEnum, Observation, ObservationSource
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker
from app.knowledge_base.boot import BOOT_CAUSES, BOOT_SYMPTOMS

client = TestClient(app)


def test_boot_knowledge_base_structure():
    """
    Verifies that BOOT_CAUSES and BOOT_SYMPTOMS are properly structured.
    """
    assert len(BOOT_CAUSES) >= 5
    assert "slow_boot_time" in BOOT_SYMPTOMS
    assert "stuck_on_logo" in BOOT_SYMPTOMS
    assert "boot_error_screen" in BOOT_SYMPTOMS

    for cause in BOOT_CAUSES:
        assert "cause_id" in cause
        assert "symptom_weights" in cause
        assert "fix_steps" in cause
        assert len(cause["fix_steps"]) >= 2


def test_boot_evaluator_startup_app_overload():
    """
    Evaluates boot observations for startup app overload scenario.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.BOOT_FAILURE)
    ranker = CauseRanker()

    obs = [
        Observation(key="slow_desktop_usable", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
        Observation(key="slow_boot_time", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
    ]

    evaluated = evaluator.evaluate(obs)
    obs_map = {o.key: o for o in obs}
    ranked = ranker.rank_causes(evaluated, obs_map)

    assert len(ranked) > 0
    top_cause = ranked[0]
    assert top_cause.cause_id == "cause_startup_app_overload"
    assert top_cause.confidence_score >= 0.70


def test_boot_evaluator_boot_file_corruption():
    """
    Evaluates boot observations for BCD / boot file corruption.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.BOOT_FAILURE)
    ranker = CauseRanker()

    obs = [
        Observation(key="boot_error_screen", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
        Observation(key="reboot_loop", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
    ]

    evaluated = evaluator.evaluate(obs)
    obs_map = {o.key: o for o in obs}
    ranked = ranker.rank_causes(evaluated, obs_map)

    assert len(ranked) > 0
    cause_ids = [c.cause_id for c in ranked]
    assert "cause_boot_file_corruption" in cause_ids


def test_boot_evaluator_peripheral_conflict():
    """
    Evaluates boot observations for external USB drive conflicts.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.BOOT_FAILURE)
    ranker = CauseRanker()

    obs = [
        Observation(key="external_drives_connected", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
        Observation(key="stuck_on_logo", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
    ]

    evaluated = evaluator.evaluate(obs)
    obs_map = {o.key: o for o in obs}
    ranked = ranker.rank_causes(evaluated, obs_map)

    assert len(ranked) > 0
    assert ranked[0].cause_id == "cause_peripheral_boot_conflict"


def test_boot_api_evaluation_endpoint():
    """
    Tests POST /api/diagnostic/evaluate for boot_failure domain via FastAPI TestClient.
    """
    # 1. Create boot failure session
    create_res = client.post("/api/session", json={"domain": "boot_failure"})
    assert create_res.status_code == 201
    session_id = create_res.json()["session_id"]
    assert create_res.json()["domain"] == "boot_failure"

    # 2. Evaluate diagnostic for boot domain
    eval_payload = {
        "session_id": session_id,
        "domain": "boot_failure",
        "text_input": "My PC takes over 5 minutes to boot into Windows and stays stuck on the boot logo",
        "observations": [
            {"key": "slow_boot_time", "value": True, "confidence": 1.0, "source": "user_input"},
            {"key": "stuck_on_logo", "value": True, "confidence": 1.0, "source": "user_input"}
        ]
    }
    eval_res = client.post("/api/diagnostic/evaluate", json=eval_payload)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()

    assert eval_data["domain"] == "boot_failure"
    assert len(eval_data["ranked_causes"]) > 0

    # 3. Retrieve session and verify stored boot domain state
    get_res = client.get(f"/api/session/{session_id}")
    assert get_res.status_code == 200
    session_data = get_res.json()
    assert session_data["domain"] == "boot_failure"
    assert session_data["status"] == "in_progress"
    assert len(session_data["ranked_causes"]) > 0


def test_boot_unknown_or_insufficient_symptoms():
    """
    Verifies that insufficient symptoms do not rank causes above threshold.
    """
    evaluator = ExpertEvaluator(domain=DomainEnum.BOOT_FAILURE)
    ranker = CauseRanker()

    obs = [
        Observation(key="unknown_symptom_key", value=True, confidence=1.0, source=ObservationSource.USER_INPUT)
    ]

    evaluated = evaluator.evaluate(obs)
    obs_map = {o.key: o for o in obs}
    ranked = ranker.rank_causes(evaluated, obs_map)

    assert len(ranked) == 0
