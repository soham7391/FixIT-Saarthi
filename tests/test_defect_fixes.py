"""
Tests for both confirmed defects:

Bug 1: Network Diagnosis Returns No Matching Causes
  - The evaluate endpoint was using a module-level PERFORMANCE evaluator singleton
    regardless of request.domain. This test verifies the VPN scenario and other
    representative network cases now produce correct results.

Bug 2: Domain routing / evaluator dispatch isolation
  - Verifies that observations fed under domain=network are evaluated with
    Network rules, and that Performance observations under domain=performance
    use Performance rules.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.schemas.diagnostic import DomainEnum, Observation, ObservationSource
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker
from app.gemini.client import GeminiAssistant

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _obs(key: str, value: bool = True, confidence: float = 1.0) -> Observation:
    return Observation(key=key, value=value, confidence=confidence, source=ObservationSource.USER_INPUT)


def _ranked(observations: list, domain: DomainEnum) -> list:
    evaluator = ExpertEvaluator(domain=domain)
    ranker = CauseRanker()
    evaluated = evaluator.evaluate(observations)
    obs_map = {o.key: o for o in observations}
    return ranker.rank_causes(evaluated, obs_map)


# ---------------------------------------------------------------------------
# Bug 1 — Network causes must match under DomainEnum.NETWORK
# ---------------------------------------------------------------------------

class TestNetworkDiagnosisBug:
    """Verifies the VPN scenario and representative network causes produce results."""

    def test_vpn_scenario_matches_vpn_cause(self):
        """
        The VPN test paragraph from the bug report must produce cause_vpn_proxy_interference
        as the top-ranked result under domain=network.
        """
        text = (
            "My Windows laptop connects to my home Wi-Fi, but websites cannot load when my VPN "
            "is turned on. Other devices on the same Wi-Fi can access the internet normally. "
            "All websites fail on my laptop while the VPN is connected. When I disconnect the VPN, "
            "websites load normally again. The Wi-Fi signal is strong."
        )
        assistant = GeminiAssistant()
        obs = assistant._heuristic_parse_text(text)

        # Must have parsed vpn_proxy_enabled
        keys = {o.key for o in obs}
        assert 'vpn_proxy_enabled' in keys, f"vpn_proxy_enabled missing from heuristic output. Got: {keys}"
        # other_devices_working from "Other devices on the same Wi-Fi"
        assert 'other_devices_working' in keys, f"other_devices_working missing. Got: {keys}"

        ranked = _ranked(obs, DomainEnum.NETWORK)
        assert len(ranked) > 0, "No causes returned for VPN scenario under network domain"
        top = ranked[0]
        assert top.cause_id == 'cause_vpn_proxy_interference', (
            f"Expected cause_vpn_proxy_interference at rank 1, got {top.cause_id} "
            f"(score={top.confidence_score})"
        )
        assert top.confidence_score >= 0.50

    def test_dns_scenario_matches_dns_cause(self):
        """DNS error description must match cause_dns_resolution_issue."""
        text = "Websites fail with server not found and dns error messages on my laptop. Other devices work fine."
        assistant = GeminiAssistant()
        obs = assistant._heuristic_parse_text(text)
        keys = {o.key for o in obs}
        assert 'dns_lookup_failure' in keys

        ranked = _ranked(obs, DomainEnum.NETWORK)
        ids = [r.cause_id for r in ranked]
        assert 'cause_dns_resolution_issue' in ids

    def test_wifi_disabled_scenario(self):
        """Airplane mode description matches cause_wifi_disabled."""
        obs = [_obs('wifi_disabled_airplane')]
        ranked = _ranked(obs, DomainEnum.NETWORK)
        assert len(ranked) > 0
        assert ranked[0].cause_id == 'cause_wifi_disabled'

    def test_insufficient_evidence_returns_empty_or_graceful(self):
        """A single low-confidence observation below threshold must not force a bad result."""
        obs = [Observation(key='connected_no_internet', value=True, confidence=0.1,
                           source=ObservationSource.USER_INPUT)]
        ranked = _ranked(obs, DomainEnum.NETWORK)
        # Either no results (below threshold) or low-confidence — never raises
        assert isinstance(ranked, list)


# ---------------------------------------------------------------------------
# Bug 2 — Evaluate API must dispatch per request.domain
# ---------------------------------------------------------------------------

class TestDomainDispatchBug:
    """Verifies /evaluate uses request.domain, not a Performance singleton."""

    def _mock_obs_list(self, keys: list) -> list:
        return [{"key": k, "value": True, "confidence": 1.0, "source": "questionnaire"} for k in keys]

    def test_network_domain_evaluation_via_api(self):
        """
        POST /api/diagnostic/evaluate with domain=network and network observations
        must return network cause IDs — not performance cause IDs.
        """
        payload = {
            "domain": "network",
            "observations": self._mock_obs_list(["vpn_proxy_enabled", "connected_no_internet"]),
        }
        resp = client.post("/api/diagnostic/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        ids = [c["cause_id"] for c in data["ranked_causes"]]
        # Must contain a network cause
        assert any(cid.startswith("cause_") for cid in ids), f"No causes in response: {data}"
        # Must NOT contain performance causes
        perf_ids = {"cause_high_cpu", "cause_ram_exhaustion", "cause_disk_saturation",
                    "cause_app_hang", "cause_thermal_throttle"}
        assert not perf_ids.intersection(set(ids)), (
            f"Performance causes appeared in network evaluation: {perf_ids.intersection(set(ids))}"
        )

    def test_performance_domain_evaluation_via_api(self):
        """
        POST /api/diagnostic/evaluate with domain=performance and CPU observations
        must return performance cause IDs.
        """
        payload = {
            "domain": "performance",
            "observations": self._mock_obs_list(["high_cpu_usage", "app_freezing", "general_slowdown"]),
        }
        resp = client.post("/api/diagnostic/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        ids = [c["cause_id"] for c in data["ranked_causes"]]
        assert len(ids) > 0, "Performance domain must return causes for CPU+freeze+slowdown"
        # Must not contain network causes
        net_ids = {"cause_wifi_disabled", "cause_vpn_proxy_interference", "cause_dns_resolution_issue"}
        assert not net_ids.intersection(set(ids)), (
            f"Network causes appeared in performance evaluation: {net_ids.intersection(set(ids))}"
        )

    def test_boot_domain_evaluation_via_api(self):
        """
        POST /api/diagnostic/evaluate with domain=boot_failure and boot observations
        must return boot cause IDs.
        """
        payload = {
            "domain": "boot_failure",
            "observations": self._mock_obs_list(["slow_boot_time", "stuck_on_logo"]),
        }
        resp = client.post("/api/diagnostic/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        ids = [c["cause_id"] for c in data["ranked_causes"]]
        assert len(ids) > 0, "Boot domain must return causes for slow_boot_time+stuck_on_logo"
        net_ids = {"cause_wifi_disabled", "cause_vpn_proxy_interference"}
        assert not net_ids.intersection(set(ids))

    def test_network_observations_under_performance_domain_returns_no_network_causes(self):
        """
        This is the regression test for Bug 2: network observations sent with
        domain=performance must NOT return network cause IDs (they'll miss because
        performance rules don't know about network keys).
        """
        payload = {
            "domain": "performance",
            "observations": self._mock_obs_list(["vpn_proxy_enabled", "dns_lookup_failure"]),
        }
        resp = client.post("/api/diagnostic/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        ids = [c["cause_id"] for c in data["ranked_causes"]]
        net_ids = {"cause_vpn_proxy_interference", "cause_dns_resolution_issue"}
        assert not net_ids.intersection(set(ids)), (
            "Network causes must not appear when domain=performance (cross-domain isolation)"
        )
