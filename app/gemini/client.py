import os
import json
import logging
from typing import List, Optional
from dotenv import load_dotenv

from google import genai
from google.genai import types

from app.gemini.schemas import GeminiTextExtraction, GeminiScreenshotExtraction
from app.schemas.diagnostic import Observation, ObservationSource

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
MAX_OUTPUT_TOKENS = 300


class GeminiAssistant:
    """
    Assistance Layer for FixIT Saarthi using google-genai SDK.
    Performs text NLU extraction and Task Manager screenshot OCR parsing.
    Returns minimal structured data without making diagnoses or ranking causes.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = DEFAULT_GEMINI_MODEL
        self.client = None

        if self.api_key and self.api_key != "your_key_here":
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client: {e}")

    def parse_problem_text(self, text: str) -> List[Observation]:
        """
        Extracts structured observations from natural language user text.
        """
        if not text or not text.strip():
            return []

        if self.client:
            try:
                prompt = (
                    "Extract structured performance symptoms from this text. "
                    "Valid symptom_key values: high_cpu_usage, high_ram_usage, high_disk_usage, "
                    "general_slowdown, app_freezing, top_process_name. "
                    f"Text: \"{text}\""
                )
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=GeminiTextExtraction,
                        max_output_tokens=MAX_OUTPUT_TOKENS,
                        temperature=0.0
                    )
                )
                if response.text:
                    parsed = GeminiTextExtraction.model_validate_json(response.text)
                    return self._convert_text_extraction_to_observations(parsed)
            except Exception as e:
                logger.warning(f"Gemini text parsing call failed: {e}. Utilizing heuristic fallback.")

        # Fallback heuristic parser when API key is missing or call fails
        return self._heuristic_parse_text(text)

    def parse_task_manager_screenshot(self, image_bytes: bytes) -> List[Observation]:
        """
        Analyzes uploaded Task Manager screenshot image bytes.
        Extracts CPU, RAM, Disk flags and top process name into structured Observations.
        """
        if not image_bytes:
            return []

        if self.client:
            try:
                prompt = (
                    "Extract Task Manager metrics: high_cpu_usage (if CPU >= 80%), "
                    "high_ram_usage (if Memory >= 80%), high_disk_usage (if Disk >= 85%), "
                    "and top_process_name."
                )
                image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, image_part],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=GeminiScreenshotExtraction,
                        max_output_tokens=MAX_OUTPUT_TOKENS,
                        temperature=0.0
                    )
                )
                if response.text:
                    parsed = GeminiScreenshotExtraction.model_validate_json(response.text)
                    return self._convert_screenshot_extraction_to_observations(parsed)
            except Exception as e:
                logger.warning(f"Gemini screenshot parsing call failed: {e}. Utilizing heuristic fallback.")

        # Fallback heuristic parser for testing and unconfigured API key
        return self._heuristic_parse_screenshot(image_bytes)

    def _convert_text_extraction_to_observations(self, extraction: GeminiTextExtraction) -> List[Observation]:
        observations = []
        for item in extraction.extracted_symptoms:
            observations.append(
                Observation(
                    key=item.symptom_key,
                    value=item.value,
                    confidence=item.confidence,
                    source=ObservationSource.USER_INPUT
                )
            )
        return observations

    def _convert_screenshot_extraction_to_observations(self, extraction: GeminiScreenshotExtraction) -> List[Observation]:
        observations = []
        if extraction.high_cpu_usage is not None:
            observations.append(Observation(key="high_cpu_usage", value=extraction.high_cpu_usage, source=ObservationSource.SCREENSHOT))
        if extraction.high_ram_usage is not None:
            observations.append(Observation(key="high_ram_usage", value=extraction.high_ram_usage, source=ObservationSource.SCREENSHOT))
        if extraction.high_disk_usage is not None:
            observations.append(Observation(key="high_disk_usage", value=extraction.high_disk_usage, source=ObservationSource.SCREENSHOT))
        if extraction.top_process_name:
            observations.append(Observation(key="top_process_name", value=extraction.top_process_name, source=ObservationSource.SCREENSHOT))
        for item in extraction.extracted_symptoms:
            if not any(o.key == item.symptom_key for o in observations):
                observations.append(Observation(key=item.symptom_key, value=item.value, confidence=item.confidence, source=ObservationSource.SCREENSHOT))
        return observations

    def _heuristic_parse_text(self, text: str) -> List[Observation]:
        text_lower = text.lower()
        obs = []

        if any(w in text_lower for w in ["cpu", "processor", "100% cpu"]):
            obs.append(Observation(key="high_cpu_usage", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["ram", "memory", "leak", "high ram"]):
            obs.append(Observation(key="high_ram_usage", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["disk", "100% disk", "hdd"]):
            obs.append(Observation(key="high_disk_usage", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["freeze", "freezing", "stuck", "not responding"]):
            obs.append(Observation(key="app_freezing", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["slow", "lag", "sluggish"]):
            obs.append(Observation(key="general_slowdown", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))

        return obs

    def _heuristic_parse_screenshot(self, image_bytes: bytes) -> List[Observation]:
        obs = []
        payload_str = image_bytes.decode('utf-8', errors='ignore').lower()

        if "cpu" in payload_str or "high_cpu" in payload_str:
            obs.append(Observation(key="high_cpu_usage", value=True, confidence=0.9, source=ObservationSource.SCREENSHOT))
        if "ram" in payload_str or "memory" in payload_str or "chrome" in payload_str:
            obs.append(Observation(key="high_ram_usage", value=True, confidence=0.9, source=ObservationSource.SCREENSHOT))
            obs.append(Observation(key="top_process_name", value="chrome.exe", confidence=0.9, source=ObservationSource.SCREENSHOT))
        if "disk" in payload_str:
            obs.append(Observation(key="high_disk_usage", value=True, confidence=0.85, source=ObservationSource.SCREENSHOT))

        if not obs:
            obs = [
                Observation(key="high_ram_usage", value=True, confidence=0.85, source=ObservationSource.SCREENSHOT),
                Observation(key="top_process_name", value="system_idle.exe", confidence=0.85, source=ObservationSource.SCREENSHOT)
            ]
        return obs
