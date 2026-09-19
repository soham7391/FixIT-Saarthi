import os
import re
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv

try:
    from supabase import create_client
except ImportError:
    create_client = None

from app.schemas.diagnostic import (
    SessionResponse,
    DomainEnum,
    Observation,
    RankedCause
)

# Load .env relative to THIS file's directory so it works regardless of CWD
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

logger = logging.getLogger(__name__)

# Fallback in-memory store — used ONLY when credentials are genuinely unavailable
_IN_MEMORY_SESSIONS: Dict[str, Dict[str, Any]] = {}

_URL_PATTERN = re.compile(r"^https://[a-zA-Z0-9\-]+\.supabase\.co/?$")


def _validate_supabase_url(url: str) -> bool:
    """Returns True if url looks like a valid Supabase project URL."""
    return bool(url and _URL_PATTERN.match(url.rstrip("/")))


class SupabaseSessionManager:
    """
    Isolated Supabase persistence manager for troubleshooting sessions.
    Interacts with public.troubleshooting_sessions table.

    In-memory fallback is only used when credentials are genuinely unavailable
    (env vars missing or empty). Real Supabase errors are raised so they are
    visible — they are NOT silently swallowed into the fallback.
    """

    def __init__(self, url: Optional[str] = None, secret_key: Optional[str] = None):
        raw_url = (url or os.getenv("SUPABASE_URL", "")).strip()
        raw_key = (
            secret_key or
            os.getenv("SUPABASE_SECRET_KEY", "") or
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or
            os.getenv("SUPABASE_KEY", "")
        ).strip()

        self.client = None
        self._use_memory = False

        if not raw_url or not raw_key:
            logger.info("Supabase credentials not set — using in-memory session store.")
            self._use_memory = True
            return

        if not _validate_supabase_url(raw_url):
            logger.error(
                "SUPABASE_URL does not look like a valid Supabase project URL "
                "(expected https://<project>.supabase.co). "
                "Check your .env — you may have a publishable/anon key set in SUPABASE_URL instead of the URL. "
                "Falling back to in-memory store until this is corrected."
            )
            self._use_memory = True
            return

        if create_client is None:
            logger.error("supabase package is not installed — pip install supabase")
            self._use_memory = True
            return

        try:
            self.client = create_client(raw_url, raw_key)
            logger.info("Supabase client initialised successfully.")
        except Exception as e:
            logger.error(
                f"Failed to create Supabase client ({type(e).__name__}: {e}). "
                "Check SUPABASE_URL and SUPABASE_SECRET_KEY in .env."
            )
            self._use_memory = True

    # ------------------------------------------------------------------ #
    #  Public CRUD methods                                                 #
    # ------------------------------------------------------------------ #

    def create_session(self, domain: DomainEnum = DomainEnum.PERFORMANCE) -> SessionResponse:
        """Creates a new active troubleshooting session."""
        session_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        session_data: Dict[str, Any] = {
            "session_id": session_id,
            "domain": domain.value if isinstance(domain, DomainEnum) else str(domain),
            "observations": [],
            "ranked_causes": [],
            "status": "active",
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        if self.client:
            try:
                res = self.client.table("troubleshooting_sessions").insert(session_data).execute()
                if res.data and len(res.data) > 0:
                    session_data = res.data[0]
                    logger.info(f"Session {session_id[:8]}… created in Supabase.")
                else:
                    raise RuntimeError("Insert returned no data — check table RLS policies.")
            except Exception as e:
                raise RuntimeError(
                    f"Supabase insert failed ({type(e).__name__}): {e}. "
                    "Verify the table exists and Row Level Security allows inserts with your key."
                ) from e
        else:
            _IN_MEMORY_SESSIONS[session_id] = session_data

        return self._format_session_response(session_data)

    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Retrieves a session by ID. Returns None if not found."""
        if not session_id or not session_id.strip():
            return None

        if self.client:
            try:
                res = (
                    self.client.table("troubleshooting_sessions")
                    .select("*")
                    .eq("session_id", session_id)
                    .execute()
                )
                if res.data and len(res.data) > 0:
                    return self._format_session_response(res.data[0])
                return None
            except Exception as e:
                err_msg = str(e)
                if "22P02" in err_msg or "invalid input syntax for type uuid" in err_msg:
                    return None
                raise RuntimeError(
                    f"Supabase fetch failed ({type(e).__name__}): {e}."
                ) from e
        else:
            raw = _IN_MEMORY_SESSIONS.get(session_id)
            return self._format_session_response(raw) if raw else None

    def update_session(
        self,
        session_id: str,
        observations: List[Observation],
        ranked_causes: List[RankedCause],
        status: str = "in_progress",
    ) -> Optional[SessionResponse]:
        """Updates a session's observations, ranked causes, status, and updated_at."""
        if not session_id or not session_id.strip():
            return None

        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "observations": [o.model_dump() for o in observations],
            "ranked_causes": [c.model_dump() for c in ranked_causes],
            "status": status,
            "updated_at": now_iso,
        }

        if self.client:
            try:
                res = (
                    self.client.table("troubleshooting_sessions")
                    .update(payload)
                    .eq("session_id", session_id)
                    .execute()
                )
                if res.data and len(res.data) > 0:
                    return self._format_session_response(res.data[0])
                return None
            except Exception as e:
                err_msg = str(e)
                if "22P02" in err_msg or "invalid input syntax for type uuid" in err_msg:
                    return None
                raise RuntimeError(
                    f"Supabase update failed ({type(e).__name__}): {e}."
                ) from e
        else:
            if session_id in _IN_MEMORY_SESSIONS:
                _IN_MEMORY_SESSIONS[session_id].update(payload)
                return self._format_session_response(_IN_MEMORY_SESSIONS[session_id])
            return None

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _format_session_response(self, data: dict) -> SessionResponse:
        obs_raw = data.get("observations", [])
        causes_raw = data.get("ranked_causes", [])

        if isinstance(obs_raw, dict):
            obs_list = [Observation(**v) if isinstance(v, dict) else v for v in obs_raw.values()]
        elif isinstance(obs_raw, list):
            obs_list = [Observation(**o) if isinstance(o, dict) else o for o in obs_raw]
        else:
            obs_list = []

        causes_list = [
            RankedCause(**c) if isinstance(c, dict) else c
            for c in (causes_raw or [])
        ]

        return SessionResponse(
            session_id=data["session_id"],
            domain=DomainEnum(data.get("domain", "performance")),
            observations=obs_list,
            ranked_causes=causes_list,
            status=data.get("status", "active"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
