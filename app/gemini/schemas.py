from typing import List, Optional, Any
from pydantic import BaseModel, Field


class ExtractedSymptomItem(BaseModel):
    symptom_key: str = Field(..., description="Symptom key: high_cpu_usage, high_ram_usage, high_disk_usage, general_slowdown, app_freezing, top_process_name")
    value: Any = Field(..., description="Extracted boolean, percentage number, or string value")
    confidence: float = Field(0.9, ge=0.0, le=1.0, description="Confidence score")


class GeminiTextExtraction(BaseModel):
    extracted_symptoms: List[ExtractedSymptomItem] = Field(default_factory=list, description="Extracted symptoms")


class GeminiScreenshotExtraction(BaseModel):
    high_cpu_usage: Optional[bool] = Field(None, description="True if CPU >= 80%")
    high_ram_usage: Optional[bool] = Field(None, description="True if Memory >= 80%")
    high_disk_usage: Optional[bool] = Field(None, description="True if Disk >= 85%")
    top_process_name: Optional[str] = Field(None, description="Top resource consuming process name")
    extracted_symptoms: List[ExtractedSymptomItem] = Field(default_factory=list, description="Extracted symptoms list")
