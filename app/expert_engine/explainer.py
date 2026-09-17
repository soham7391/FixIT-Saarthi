from typing import Dict, Any, List
from app.schemas.diagnostic import Observation


class ExpertExplainer:
    """
    Generates human-readable explanations explaining why causes matched.
    """

    def generate_reasoning(self, candidate: Dict[str, Any], observations_map: Dict[str, Observation]) -> str:
        matched_keys = candidate.get("matched_symptoms", [])
        template = candidate.get("explanation_template", "")

        cpu_val = str(observations_map["high_cpu_usage"].value) if "high_cpu_usage" in observations_map else "High"
        ram_val = str(observations_map["high_ram_usage"].value) if "high_ram_usage" in observations_map else "High"
        top_proc = str(observations_map["top_process_name"].value) if "top_process_name" in observations_map else "a background process"

        try:
            formatted = template.format(
                cpu_pct=cpu_val,
                ram_pct=ram_val,
                top_process=top_proc
            )
        except Exception:
            formatted = candidate.get("description", "")

        readable_matched = [key.replace("_", " ").title() for key in matched_keys]
        evidence_str = f" Matched evidence: {', '.join(readable_matched)}." if readable_matched else ""

        return f"{formatted}{evidence_str}"
