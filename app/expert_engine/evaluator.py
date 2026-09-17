from typing import List, Dict, Any
from app.schemas.diagnostic import Observation, DomainEnum
from app.knowledge_base.performance import PERFORMANCE_CAUSES, PERFORMANCE_SYMPTOMS


class ExpertEvaluator:
    """
    Deterministic rule evaluator for computer troubleshooting.
    Matches observations against domain rules and computes matching scores.
    """

    def __init__(self, domain: DomainEnum = DomainEnum.PERFORMANCE):
        self.domain = domain
        self.causes = self._load_causes(domain)
        self.symptoms_def = self._load_symptoms_def(domain)

    def _load_causes(self, domain: DomainEnum) -> List[Dict[str, Any]]:
        if domain == DomainEnum.PERFORMANCE:
            return PERFORMANCE_CAUSES
        return []

    def _load_symptoms_def(self, domain: DomainEnum) -> Dict[str, Dict[str, Any]]:
        if domain == DomainEnum.PERFORMANCE:
            return PERFORMANCE_SYMPTOMS
        return {}

    def parse_symptom_value(self, obs: Observation) -> bool:
        """
        Parses observation values into boolean symptom presence.
        Supports boolean inputs, percentage numbers (>= 75%), and string state flags.
        """
        val = obs.value
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            if "cpu" in obs.key and val >= 75.0:
                return True
            if "ram" in obs.key and val >= 75.0:
                return True
            if "disk" in obs.key and val >= 85.0:
                return True
            return val > 0
        if isinstance(val, str):
            val_lower = val.strip().lower()
            return val_lower in ["true", "yes", "high", "active", "stuck", "freezing"]
        return bool(val)

    def evaluate(self, observations: List[Observation]) -> List[Dict[str, Any]]:
        """
        Evaluates observations against candidate causes.
        Calculates matched symptom weights and returns raw candidate cause evaluation objects.
        """
        obs_map: Dict[str, Observation] = {obs.key: obs for obs in observations}
        active_symptoms: Dict[str, Observation] = {}

        for key, obs in obs_map.items():
            if self.parse_symptom_value(obs):
                active_symptoms[key] = obs

        evaluation_results = []

        for cause in self.causes:
            matched_symptoms = []
            matched_score = 0.0
            total_possible_weight = sum(cause["symptom_weights"].values())

            for symptom_key, weight in cause["symptom_weights"].items():
                if symptom_key in active_symptoms:
                    obs = active_symptoms[symptom_key]
                    matched_score += weight * obs.confidence
                    matched_symptoms.append(symptom_key)

            normalized_score = (matched_score / total_possible_weight) if total_possible_weight > 0 else 0.0

            evaluation_results.append({
                "cause_id": cause["cause_id"],
                "cause_name": cause["cause_name"],
                "description": cause.get("description", ""),
                "raw_score": matched_score,
                "confidence_score": round(normalized_score, 2),
                "matched_symptoms": matched_symptoms,
                "min_threshold": cause.get("min_threshold", 0.3),
                "explanation_template": cause.get("explanation", ""),
                "fix_steps": cause.get("fix_steps", [])
            })

        return evaluation_results
