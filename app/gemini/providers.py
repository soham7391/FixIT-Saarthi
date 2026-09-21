import os
import base64
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

from google.genai import types

try:
    import groq
    from groq import Groq
except ImportError:
    groq = None
    Groq = None

from app.gemini.schemas import GeminiTextExtraction, GeminiScreenshotExtraction

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
MAX_OUTPUT_TOKENS = 300


class TransientProviderError(Exception):
    """Exception raised when an AI provider fails due to 429, 5xx, or network/timeout issues."""
    pass


class BaseAIProvider(ABC):
    """Abstract interface for AI Providers returning structured Pydantic extractions."""

    @abstractmethod
    def extract_text(self, text: str) -> GeminiTextExtraction:
        pass

    @abstractmethod
    def extract_screenshot(self, image_bytes: bytes, mime_type: str = "image/png") -> GeminiScreenshotExtraction:
        pass


class GeminiProvider(BaseAIProvider):
    """Primary AI provider using google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_GEMINI_MODEL):
        from app.gemini.client import genai  # Shared reference so @patch("app.gemini.client.genai.Client") works in tests

        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name
        self.client = None

        if self.api_key and self.api_key != "your_key_here" and genai is not None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client: {e}")

    def extract_text(self, text: str) -> GeminiTextExtraction:
        if not self.client:
            raise TransientProviderError("Gemini client is not configured or initialized.")

        prompt = (
            "Extract structured performance symptoms from this text into JSON. "
            "Valid symptom_key values: high_cpu_usage, high_ram_usage, high_disk_usage, "
            "general_slowdown, app_freezing, top_process_name. "
            f"Text: \"{text}\""
        )
        try:
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
            if not response or not getattr(response, "text", None):
                raise TransientProviderError("Gemini returned empty response text.")

            return GeminiTextExtraction.model_validate_json(response.text)
        except Exception as e:
            logger.warning(f"GeminiProvider.extract_text failed: {type(e).__name__}: {e}")
            raise TransientProviderError(f"Gemini API error: {e}") from e

    def extract_screenshot(self, image_bytes: bytes, mime_type: str = "image/png") -> GeminiScreenshotExtraction:
        if not self.client:
            raise TransientProviderError("Gemini client is not configured or initialized.")

        prompt = (
            "Extract Task Manager metrics: high_cpu_usage (if CPU >= 80%), "
            "high_ram_usage (if Memory >= 80%), high_disk_usage (if Disk >= 85%), "
            "and top_process_name."
        )
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
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
            if not response or not getattr(response, "text", None):
                raise TransientProviderError("Gemini returned empty response text.")

            return GeminiScreenshotExtraction.model_validate_json(response.text)
        except Exception as e:
            logger.warning(f"GeminiProvider.extract_screenshot failed: {type(e).__name__}: {e}")
            raise TransientProviderError(f"Gemini API error: {e}") from e


class GroqProvider(BaseAIProvider):
    """Backup AI provider using groq SDK (Model: qwen/qwen3.8-27b)."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_GROQ_MODEL):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.model_name = model_name
        self.client = None

        if self.api_key and self.api_key != "your_key_here" and Groq is not None:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

    def extract_text(self, text: str) -> GeminiTextExtraction:
        if not self.client:
            raise TransientProviderError("Groq client is not configured or initialized.")

        prompt = (
            "You are a computer performance symptom extractor. Extract symptoms from user input. "
            "Respond ONLY with a valid JSON object following this schema: "
            '{"extracted_symptoms": [{"symptom_key": "high_cpu_usage|high_ram_usage|high_disk_usage|general_slowdown|app_freezing|top_process_name", "value": true/false/string, "confidence": 0.9}]}. '
            f'User Text: "{text}"'
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Return JSON only. Do not diagnose or make troubleshooting decisions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=MAX_OUTPUT_TOKENS,
                extra_body={"reasoning_format": "hidden"}
            )

            content = response.choices[0].message.content
            if not content:
                raise TransientProviderError("Groq returned empty response content.")

            return GeminiTextExtraction.model_validate_json(content)
        except Exception as e:
            logger.warning(f"GroqProvider.extract_text failed: {type(e).__name__}: {e}")
            raise TransientProviderError(f"Groq API error: {e}") from e

    def extract_screenshot(self, image_bytes: bytes, mime_type: str = "image/png") -> GeminiScreenshotExtraction:
        if not self.client:
            raise TransientProviderError("Groq client is not configured or initialized.")

        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_img}"

        prompt = (
            "Extract Task Manager metrics into JSON: high_cpu_usage (if CPU >= 80%), "
            "high_ram_usage (if Memory >= 80%), high_disk_usage (if Disk >= 85%), "
            "and top_process_name. "
            'Schema: {"high_cpu_usage": bool, "high_ram_usage": bool, "high_disk_usage": bool, "top_process_name": "name", "extracted_symptoms": []}'
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Return JSON only."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}}
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=MAX_OUTPUT_TOKENS,
                extra_body={"reasoning_format": "hidden"}
            )

            content = response.choices[0].message.content
            if not content:
                raise TransientProviderError("Groq returned empty response content.")

            return GeminiScreenshotExtraction.model_validate_json(content)
        except Exception as e:
            logger.warning(f"GroqProvider.extract_screenshot failed: {type(e).__name__}: {e}")
            raise TransientProviderError(f"Groq API error: {e}") from e
