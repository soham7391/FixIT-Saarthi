from typing import List, Dict, Any
from app.schemas.diagnostic import RankedCause, FixStep
from app.expert_engine.explainer import ExpertExplainer


class CauseRanker:
    """
    Normalizes confidence scores, filters below-threshold causes,
    and ranks causes descending by confidence score.
    """

    def __init__(self):
        self.explainer = ExpertExplainer()

    def rank_causes(self, evaluated_candidates: List[Dict[str, Any]], observations_map: Dict[str, Any]) -> List[RankedCause]:
        valid_causes = []
        top_proc = str(observations_map["top_process_name"].value) if "top_process_name" in observations_map else "high-resource process"

        for candidate in evaluated_candidates:
            confidence = candidate["confidence_score"]
            threshold = candidate["min_threshold"]

            if confidence >= threshold and candidate["matched_symptoms"]:
                reasoning = self.explainer.generate_reasoning(candidate, observations_map)

                # Format process name in fix steps if top_process_name is available
                formatted_fix_steps: List[FixStep] = []
                for step in candidate["fix_steps"]:
                    instruction = step.instruction.replace("{top_process}", top_proc)
                    formatted_fix_steps.append(
                        FixStep(
                            step_number=step.step_number,
                            title=step.title,
                            instruction=instruction,
                            safety_level=step.safety_level,
                            warning_note=step.warning_note,
                            verification_question=step.verification_question
                        )
                    )

                ranked_cause = RankedCause(
                    cause_id=candidate["cause_id"],
                    cause_name=candidate["cause_name"],
                    confidence_score=confidence,
                    matched_symptoms=candidate["matched_symptoms"],
                    reasoning=reasoning,
                    fix_steps=formatted_fix_steps
                )
                valid_causes.append(ranked_cause)

        valid_causes.sort(key=lambda x: x.confidence_score, reverse=True)
        return valid_causes
