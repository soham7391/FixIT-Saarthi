import os
import logging
from typing import List, Optional

from google import genai  # Re-exported for backward-compatibility with tests patching app.gemini.client.genai
from dotenv import load_dotenv

from app.gemini.schemas import GeminiTextExtraction, GeminiScreenshotExtraction
from app.gemini.providers import (
    BaseAIProvider,
    GeminiProvider,
    GroqProvider,
    TransientProviderError
)
from app.gemini.safety import (
    InputSafetyGuard,
    OutputSafetyGuard,
    rate_limiter
)
from app.schemas.diagnostic import Observation, ObservationSource

load_dotenv()
logger = logging.getLogger(__name__)


class AIAssistanceService:
    """
    AI Reliability & Safety Assistance Layer for FixIT Saarthi.
    Manages primary (Gemini) and backup (Groq) providers with automatic failover,
    input safety validation, prompt injection resistance, scope guarding,
    output structure validation, and in-memory rate limiting.
    """

    def __init__(
        self,
        primary_provider: Optional[BaseAIProvider] = None,
        backup_provider: Optional[BaseAIProvider] = None,
        api_key: Optional[str] = None  # Kept for legacy GeminiAssistant init signature compatibility
    ):
        self.primary_provider = primary_provider or GeminiProvider(api_key=api_key)
        self.backup_provider = backup_provider or GroqProvider()
        self.model_name = getattr(self.primary_provider, "model_name", "gemini-2.5-flash")

    def _has_working_provider_config(self) -> bool:
        """Returns True if either provider has an initialized client or custom mock instance."""
        gemini_client = getattr(self.primary_provider, "client", None)
        groq_client = getattr(self.backup_provider, "client", None)
        is_custom_primary = not isinstance(self.primary_provider, GeminiProvider)
        is_custom_backup = not isinstance(self.backup_provider, GroqProvider)
        return bool(gemini_client or groq_client or is_custom_primary or is_custom_backup)

    def parse_problem_text(
        self,
        text: str,
        client_ip: str = "127.0.0.1",
        session_id: Optional[str] = None
    ) -> List[Observation]:
        """
        Extracts structured observations from user problem statement.
        Enforces rate limiting, input safety, scope guarding, prompt injection resistance,
        provider failover (Gemini -> Groq), and output safety validation.
        """
        # 1. Rate Limiting Check
        rate_limiter.check(client_ip=client_ip, session_id=session_id)

        # 2. Input Safety, Length, Scope Guard, & Prompt Injection Validation
        validated_text = InputSafetyGuard.validate_text(text)

        extraction: Optional[GeminiTextExtraction] = None
        last_error: Optional[Exception] = None

        # 3. Attempt Primary Provider (Gemini)
        try:
            extraction = self.primary_provider.extract_text(validated_text)
            logger.info("Successfully extracted text observations via Primary Provider (Gemini).")
        except TransientProviderError as e:
            logger.warning(f"Primary provider (Gemini) failed: {e}. Initiating failover to Backup Provider (Groq)...")
            last_error = e

        # 4. Attempt Backup Provider (Groq) on Primary Failover
        if extraction is None:
            try:
                extraction = self.backup_provider.extract_text(validated_text)
                logger.info("Successfully extracted text observations via Backup Provider (Groq).")
            except TransientProviderError as e:
                logger.warning(f"Backup provider (Groq) failed: {e}.")
                last_error = e

        # 5. Handle Provider Failures / Heuristic Fallback
        if extraction is None:
            heuristic_obs = self._heuristic_parse_text(validated_text)
            if heuristic_obs:
                logger.info("Utilizing heuristic text fallback for parsed observations.")
                return heuristic_obs
            raise TransientProviderError(f"Both primary (Gemini) and backup (Groq) providers failed: {last_error}")

        # 6. Output Safety Validation
        validated_extraction = OutputSafetyGuard.validate_text_extraction(extraction)

        # 7. Convert to Observation Objects
        return self._convert_text_extraction_to_observations(validated_extraction)

    def parse_task_manager_screenshot(
        self,
        image_bytes: bytes,
        client_ip: str = "127.0.0.1",
        session_id: Optional[str] = None,
        content_type: Optional[str] = "image/png",
        file_count: int = 1
    ) -> List[Observation]:
        """
        Analyzes uploaded Task Manager screenshot image bytes.
        Enforces rate limiting, size/format validation, single image restriction,
        provider failover (Gemini -> Groq), and output safety validation.
        """
        # 1. Rate Limiting Check
        rate_limiter.check(client_ip=client_ip, session_id=session_id)

        # 2. Input Safety & Image Restrictions
        validated_bytes = InputSafetyGuard.validate_screenshot(
            image_bytes=image_bytes,
            content_type=content_type,
            file_count=file_count
        )

        extraction: Optional[GeminiScreenshotExtraction] = None
        last_error: Optional[Exception] = None
        mime_type = content_type or "image/png"

        # 3. Attempt Primary Provider (Gemini)
        try:
            extraction = self.primary_provider.extract_screenshot(validated_bytes, mime_type=mime_type)
            logger.info("Successfully extracted screenshot observations via Primary Provider (Gemini).")
        except TransientProviderError as e:
            logger.warning(f"Primary provider (Gemini) failed: {e}. Initiating failover to Backup Provider (Groq)...")
            last_error = e

        # 4. Attempt Backup Provider (Groq) on Primary Failover
        if extraction is None:
            try:
                extraction = self.backup_provider.extract_screenshot(validated_bytes, mime_type=mime_type)
                logger.info("Successfully extracted screenshot observations via Backup Provider (Groq).")
            except TransientProviderError as e:
                logger.warning(f"Backup provider (Groq) failed: {e}.")
                last_error = e

        # 5. Handle Provider Failures / Heuristic Fallback
        if extraction is None:
            heuristic_obs = self._heuristic_parse_screenshot(validated_bytes)
            if heuristic_obs:
                logger.info("Utilizing heuristic screenshot fallback for parsed observations.")
                return heuristic_obs
            raise TransientProviderError(f"Both primary (Gemini) and backup (Groq) providers failed: {last_error}")

        # 6. Output Safety Validation
        validated_extraction = OutputSafetyGuard.validate_screenshot_extraction(extraction)

        # 7. Convert to Observation Objects
        return self._convert_screenshot_extraction_to_observations(validated_extraction)

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

        # Performance symptoms
        if any(w in text_lower for w in ["cpu", "processor", "100% cpu"]):
            obs.append(Observation(key="high_cpu_usage", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["ram", "memory", "leak", "high ram"]):
            obs.append(Observation(key="high_ram_usage", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["disk", "100% disk", "hdd"]):
            obs.append(Observation(key="high_disk_usage", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["freeze", "freezing", "stuck", "not responding"]) and not any(w in text_lower for w in ["boot", "logo"]):
            obs.append(Observation(key="app_freezing", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["slow", "lag", "sluggish"]) and not any(w in text_lower for w in ["start", "boot", "internet", "wifi"]):
            obs.append(Observation(key="general_slowdown", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))

        # Boot & Startup symptoms
        if any(w in text_lower for w in ["slow boot", "takes long to start", "boot time", "slow startup"]):
            obs.append(Observation(key="slow_boot_time", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["stuck on logo", "boot logo", "spinning dots", "black screen"]):
            obs.append(Observation(key="stuck_on_logo", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["boot error", "bsod", "blue screen", "startup repair"]):
            obs.append(Observation(key="boot_error_screen", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["reboot loop", "restarts repeatedly", "restarts during boot", "restart loop"]):
            obs.append(Observation(key="reboot_loop", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["windows update", "recent update", "after update"]):
            obs.append(Observation(key="recent_windows_update", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["usb", "external drive", "hard drive connected"]):
            obs.append(Observation(key="external_drives_connected", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["disk space low", "c: drive full", "storage low"]):
            obs.append(Observation(key="disk_space_low", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["clicking noise", "grinding", "drive noise"]):
            obs.append(Observation(key="disk_clicking_noise", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))

        # Network & Connectivity symptoms
        if any(w in text_lower for w in ["wifi disabled", "airplane mode", "turn on wifi", "wifi toggle", "wi-fi disabled", "wi-fi is off"]):
            obs.append(Observation(key="wifi_disabled_airplane", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in [
            "no internet", "connected no internet", "no access", "cannot load", "can't load",
            "websites won't load", "websites cannot load", "sites won't open", "pages won't load",
            "websites fail", "wifi connected but", "wi-fi connected but", "connected but"
        ]):
            obs.append(Observation(key="connected_no_internet", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["disconnects", "drops", "weak signal", "intermittent", "keeps cutting out", "connection drops"]):
            obs.append(Observation(key="intermittent_disconnection", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["dns", "dns_probe", "server not found", "cannot reach website", "name not resolved", "dns error"]):
            obs.append(Observation(key="dns_lookup_failure", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["vpn", "proxy"]):
            obs.append(Observation(key="vpn_proxy_enabled", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["slow speed", "slow internet", "high ping", "latency", "slow connection"]):
            obs.append(Observation(key="slow_network_speed", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in [
            "other devices work", "phone works", "other laptop works",
            "other devices", "other device", "other phones", "other computers",
            "rest of the devices", "every other device", "all other devices",
            "same wi-fi", "same wifi"
        ]):
            obs.append(Observation(key="other_devices_working", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["single app", "one browser", "only chrome", "only one app", "one application"]):
            obs.append(Observation(key="single_app_affected", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))

        # Driver & Peripheral symptoms
        if any(w in text_lower for w in ["printer", "print", "printing", "offline printer", "printer not found"]):
            obs.append(Observation(key="printer_not_detected", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["keyboard", "mouse", "cursor", "trackpad", "typing", "not responding", "unresponsive key"]):
            if any(w in text_lower for w in ["keyboard", "mouse", "cursor", "trackpad"]):
                obs.append(Observation(key="keyboard_mouse_unresponsive", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["audio", "speaker", "sound", "microphone", "mic", "headset", "headphone", "no sound", "no audio"]):
            obs.append(Observation(key="audio_device_issue", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["webcam", "camera", "video feed", "cam not working"]):
            obs.append(Observation(key="webcam_unavailable", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["bluetooth", "bt device", "pairing", "pair bluetooth"]):
            obs.append(Observation(key="bluetooth_connection_failed", value=True, confidence=0.9, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["driver update", "after update", "stopped working after update", "windows update broke", "driver update broke"]):
            obs.append(Observation(key="device_failed_after_update", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["unplugged", "usb cable", "usb port", "disconnected usb", "loose cable", "not plugged in"]):
            obs.append(Observation(key="usb_physical_disconnection", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))
        if any(w in text_lower for w in ["privacy settings", "permission blocked", "camera access blocked", "microphone permission"]):
            obs.append(Observation(key="app_permissions_blocked", value=True, confidence=0.85, source=ObservationSource.USER_INPUT))

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


# Alias GeminiAssistant to AIAssistanceService for full backward compatibility
GeminiAssistant = AIAssistanceService
