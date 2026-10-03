"""Tests for the Network & Connectivity expert engine domain."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagnostic import DomainEnum, Observation, ObservationSource
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker
from app.knowledge_base.network import NETWORK_CAUSES, NETWORK_SYMPTOMS

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _obs(key: str, value: bool = True, confidence: float = 1.0) -> Observation:
    return Observation(key=key, value=value, confidence=confidence, source=ObservationSource.USER_INPUT)


def _evaluate(observations: list) -> list:
    """Run the network evaluator + ranker and return ranked causes."""
    evaluator = ExpertEvaluator(domain=DomainEnum.NETWORK)
    ranker = CauseRanker()
    evaluated = evaluator.evaluate(observations)
    obs_map = {o.key: o for o in observations}
    return ranker.rank_causes(evaluated, obs_map)


# ---------------------------------------------------------------------------
# 1. Knowledge-base structure
# ---------------------------------------------------------------------------

def test_network_knowledge_base_structure():
    """NETWORK_CAUSES and NETWORK_SYMPTOMS must be properly structured."""
    assert len(NETWORK_CAUSES) >= 4

    expected_symptom_keys = {
        'wifi_disabled_airplane',
        'connected_no_internet',
        'intermittent_disconnection',
        'dns_lookup_failure',
        'vpn_proxy_enabled',
        'slow_network_speed',
        'other_devices_working',
        'single_app_affected',
    }
    defined_keys = set(NETWORK_SYMPTOMS.keys())
    missing = expected_symptom_keys - defined_keys
    assert not missing, f"NETWORK_SYMPTOMS is missing keys: {missing}"

    for cause in NETWORK_CAUSES:
        assert "cause_id" in cause, f"{cause} missing cause_id"
        assert "symptom_weights" in cause, f"{cause} missing symptom_weights"
        assert "fix_steps" in cause, f"{cause} missing fix_steps"
        assert len(cause["fix_steps"]) >= 1


# ---------------------------------------------------------------------------
# 2. Cause matching
# ---------------------------------------------------------------------------

def test_wifi_disabled_cause_matches():
    """wifi_disabled_airplane=True should rank cause_wifi_disabled first."""
    ranked = _evaluate([_obs('wifi_disabled_airplane')])
    assert len(ranked) > 0
    assert ranked[0].cause_id == 'cause_wifi_disabled', (
        f"Expected cause_wifi_disabled at rank 1, got {ranked[0].cause_id}"
    )
    assert ranked[0].confidence_score >= 0.60


def test_dns_resolution_cause_matches():
    """dns_lookup_failure + connected_no_internet → DNS cause ranked in top 2."""
    ranked = _evaluate([
        _obs('dns_lookup_failure'),
        _obs('connected_no_internet'),
        _obs('other_devices_working'),
    ])
    cause_ids = [r.cause_id for r in ranked]
    assert 'cause_dns_resolution_issue' in cause_ids
    pos = cause_ids.index('cause_dns_resolution_issue')
    assert pos <= 1, f"Expected DNS cause in top 2, got position {pos}"


def test_vpn_interference_cause_matches():
    """vpn_proxy_enabled=True should surface cause_vpn_proxy_interference."""
    ranked = _evaluate([
        _obs('vpn_proxy_enabled'),
        _obs('connected_no_internet'),
    ])
    cause_ids = [r.cause_id for r in ranked]
    assert 'cause_vpn_proxy_interference' in cause_ids


def test_single_app_firewall_cause_matches():
    """single_app_affected=True + other_devices_working → firewall cause matched."""
    ranked = _evaluate([
        _obs('single_app_affected'),
        _obs('other_devices_working'),
    ])
    cause_ids = [r.cause_id for r in ranked]
    assert 'cause_single_app_firewall' in cause_ids


# ---------------------------------------------------------------------------
# 3. Insufficient symptoms — graceful handling
# ---------------------------------------------------------------------------

def test_no_observations_returns_list():
    """With zero observations, evaluate must return a list without raising."""
    evaluator = ExpertEvaluator(domain=DomainEnum.NETWORK)
    result = evaluator.evaluate([])
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# 4. Cross-domain isolation
# ---------------------------------------------------------------------------

def test_network_evaluator_does_not_use_performance_causes():
    """Network evaluator must not return performance cause IDs."""
    from app.knowledge_base.performance import PERFORMANCE_CAUSES

    ranked = _evaluate([_obs('wifi_disabled_airplane'), _obs('dns_lookup_failure')])
    ranked_ids = {r.cause_id for r in ranked}
    perf_ids = {c['cause_id'] for c in PERFORMANCE_CAUSES}
    overlap = ranked_ids & perf_ids
    assert not overlap, f"Network results contain performance causes: {overlap}"


def test_network_evaluator_does_not_use_boot_causes():
    """Network evaluator must not return boot cause IDs."""
    from app.knowledge_base.boot import BOOT_CAUSES

    ranked = _evaluate([_obs('connected_no_internet')])
    ranked_ids = {r.cause_id for r in ranked}
    boot_ids = {c['cause_id'] for c in BOOT_CAUSES}
    overlap = ranked_ids & boot_ids
    assert not overlap, f"Network results contain boot causes: {overlap}"


# ---------------------------------------------------------------------------
# 5. DomainEnum serialization
# ---------------------------------------------------------------------------

def test_domain_enum_network_value():
    """DomainEnum.NETWORK must serialize to the string 'network'."""
    assert DomainEnum.NETWORK.value == 'network'
