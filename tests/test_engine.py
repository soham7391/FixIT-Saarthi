import pytest
from app.schemas.diagnostic import Observation, ObservationSource, DomainEnum, SafetyLevel
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker


def test_rule_evaluation_ram_exhaustion():
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="high_ram_usage", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
        Observation(key="app_freezing", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
    ]

    obs_map = {obs.key: obs for obs in observations}
    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    top_cause = ranked[0]
    assert top_cause.cause_id in ["cause_ram_exhaustion", "cause_app_hang"]


def test_rule_evaluation_cpu_bottleneck():
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="high_cpu_usage", value=95.0, confidence=1.0, source=ObservationSource.SCREENSHOT),
        Observation(key="general_slowdown", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
    ]

    obs_map = {obs.key: obs for obs in observations}
    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    top_cause = ranked[0]
    assert top_cause.cause_id == "cause_cpu_bottleneck"


def test_rule_evaluation_disk_saturation():
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="high_disk_usage", value=True, confidence=1.0, source=ObservationSource.SCREENSHOT),
        Observation(key="general_slowdown", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
    ]

    obs_map = {obs.key: obs for obs in observations}
    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    top_cause = ranked[0]
    assert top_cause.cause_id == "cause_disk_saturation"


def test_fix_action_safety_levels():
    evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
    ranker = CauseRanker()

    observations = [
        Observation(key="high_ram_usage", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
        Observation(key="app_freezing", value=True, confidence=1.0, source=ObservationSource.USER_INPUT),
    ]
    obs_map = {obs.key: obs for obs in observations}
    raw_evals = evaluator.evaluate(observations)
    ranked = ranker.rank_causes(raw_evals, obs_map)

    assert len(ranked) > 0
    fix_steps = ranked[0].fix_steps
    assert len(fix_steps) > 0

    for step in fix_steps:
        assert isinstance(step.safety_level, SafetyLevel)
