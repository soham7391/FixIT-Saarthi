import pytest
from pydantic import ValidationError
from app.schemas.diagnostic import (
    Observation,
    ObservationSource,
    SafetyLevel,
    FixStep,
    DiagnosticRequest,
    DomainEnum
)


def test_observation_schema_validation():
    obs = Observation(
        key="high_ram_usage",
        value=True,
        confidence=0.95,
        source=ObservationSource.USER_INPUT
    )
    assert obs.key == "high_ram_usage"
    assert obs.value is True
    assert obs.confidence == 0.95


def test_fix_step_schema_validation():
    step = FixStep(
        step_number=1,
        title="Close apps",
        instruction="Close background chrome tabs.",
        safety_level=SafetyLevel.SAFE,
        verification_question="Did memory drop?"
    )
    assert step.safety_level == SafetyLevel.SAFE
    assert step.title == "Close apps"


def test_diagnostic_request_defaults():
    req = DiagnosticRequest(text_input="My laptop is freezing")
    assert req.domain == DomainEnum.PERFORMANCE
    assert req.text_input == "My laptop is freezing"
    assert req.observations == []
