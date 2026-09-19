from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class SafetyLevel(str, Enum):
    SAFE = "Safe"
    CAUTION = "Caution"
    ADVANCED = "Advanced"


class DomainEnum(str, Enum):
    PERFORMANCE = "performance"
    BOOT_FAILURE = "boot_failure"
    NETWORK = "network"


class ObservationSource(str, Enum):
    USER_INPUT = "user_input"
    SCREENSHOT = "screenshot"
    QUESTIONNAIRE = "questionnaire"


class Observation(BaseModel):
    key: str = Field(..., description="Symptom key (e.g. high_cpu_usage, high_ram_usage, high_disk_usage, general_slowdown, app_freezing, top_process_name)")
    value: Any = Field(..., description="Observed boolean, numeric, or string value")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Observation confidence score")
    source: ObservationSource = Field(ObservationSource.USER_INPUT, description="Source of the observation")
    details: Optional[str] = Field(None, description="Extra context or details")


class FixStep(BaseModel):
    step_number: int = Field(..., description="Step sequence number")
    title: str = Field(..., description="Short title of the fix action")
    instruction: str = Field(..., description="Detailed troubleshooting instruction")
    safety_level: SafetyLevel = Field(SafetyLevel.SAFE, description="Safety rating: Safe, Caution, or Advanced")
    warning_note: Optional[str] = Field(None, description="Warning for Caution or Advanced steps")
    verification_question: str = Field(..., description="Question to verify if the issue is resolved")


class RankedCause(BaseModel):
    cause_id: str = Field(..., description="Unique cause identifier")
    cause_name: str = Field(..., description="Human-readable cause name")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Normalized confidence score between 0.0 and 1.0")
    matched_symptoms: List[str] = Field(default_factory=list, description="Matched symptom keys")
    reasoning: str = Field(..., description="Explanation of why this cause matched")
    fix_steps: List[FixStep] = Field(default_factory=list, description="Recommended troubleshooting steps")


class TextParseRequest(BaseModel):
    text: Optional[str] = Field(None, description="User problem description text")
    text_input: Optional[str] = Field(None, description="Alternative field for user text")

    def get_text(self) -> str:
        return (self.text or self.text_input or "").strip()


class ScreenshotParseRequest(BaseModel):
    screenshot_base64: str = Field(..., description="Base64 encoded image string of Task Manager")


class SessionCreateRequest(BaseModel):
    domain: DomainEnum = Field(DomainEnum.PERFORMANCE, description="Troubleshooting domain")


class SessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    domain: DomainEnum = Field(DomainEnum.PERFORMANCE, description="Troubleshooting domain")
    observations: List[Observation] = Field(default_factory=list, description="Stored observations")
    ranked_causes: List[RankedCause] = Field(default_factory=list, description="Stored ranked causes")
    status: str = Field("active", description="Session status (active, in_progress, completed, resolved)")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last update timestamp")


class DiagnosticRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Optional active session ID for persistence")
    domain: DomainEnum = Field(DomainEnum.PERFORMANCE, description="Troubleshooting domain")
    text_input: Optional[str] = Field(None, description="Optional raw text description")
    screenshot_base64: Optional[str] = Field(None, description="Optional Task Manager screenshot base64")
    observations: List[Observation] = Field(default_factory=list, description="List of observed symptoms")
    top_process_name: Optional[str] = Field(None, description="Optional top process name")


class DiagnosticResponse(BaseModel):
    session_id: Optional[str] = Field(None, description="Associated session ID if applicable")
    domain: DomainEnum = Field(DomainEnum.PERFORMANCE, description="Troubleshooting domain")
    processed_observations: List[Observation] = Field(default_factory=list, description="Processed input observations")
    ranked_causes: List[RankedCause] = Field(default_factory=list, description="Ranked candidate causes")
    status: str = Field("completed", description="Status of the diagnostic evaluation")
