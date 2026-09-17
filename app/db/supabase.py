import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from app.schemas.diagnostic import SessionState, DomainEnum, Observation, RankedCause

load_dotenv()
logger = logging.getLogger(__name__)

# In-memory storage fallback for local dev & testing without Supabase credentials
_IN_MEMORY_SESSIONS: Dict[str, Dict[str, Any]] = {}


class SupabaseSessionManager:
    """
    Manages diagnostic session persistence using Supabase PostgreSQL client.
    Includes seamless in-memory fallback for local dev & testing when unconfigured.
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "").strip()
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        self.client = None

        if self.supabase_url and self.supabase_key and "your_supabase" not in self.supabase_url:
            try:
                from supabase import create_client, Client
                self.client: Optional[Client] = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase PostgreSQL client connected successfully.")
            except Exception as e:
                logger.warning(f"Failed to connect to Supabase: {e}. Utilizing in-memory session persistence.")

    def create_session(self, domain: DomainEnum = DomainEnum.PERFORMANCE) -> SessionState:
        """
        Creates a new diagnostic session.
        """
        session_id = str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()

        session_data = {
            "session_id": session_id,
            "domain": domain.value,
            "observations": {},
            "ranked_causes": [],
            "is_resolved": False,
            "created_at": now_str,
            "updated_at": now_str
        }

        if self.client:
            try:
                self.client.table("diagnostic_sessions").insert(session_data).execute()
            except Exception as e:
                logger.error(f"Supabase insert failed: {e}. Storing in memory fallback.")
                _IN_MEMORY_SESSIONS[session_id] = session_data
        else:
            _IN_MEMORY_SESSIONS[session_id] = session_data

        return SessionState(
            session_id=session_id,
            domain=domain,
            observations={},
            ranked_causes=[],
            is_resolved=False,
            created_at=now_str,
            updated_at=now_str
        )

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Retrieves an existing diagnostic session by session_id.
        """
        session_data = None

        if self.client:
            try:
                response = self.client.table("diagnostic_sessions").select("*").eq("session_id", session_id).execute()
                if response.data and len(response.data) > 0:
                    session_data = response.data[0]
            except Exception as e:
                logger.error(f"Supabase fetch failed: {e}. Checking in-memory store.")
                session_data = _IN_MEMORY_SESSIONS.get(session_id)
        else:
            session_data = _IN_MEMORY_SESSIONS.get(session_id)

        if not session_data:
            return None

        # Reconstruct Observation objects from dict
        raw_obs = session_data.get("observations", {})
        parsed_obs: Dict[str, Observation] = {}
        for key, obs_dict in raw_obs.items():
            if isinstance(obs_dict, dict):
                parsed_obs[key] = Observation(**obs_dict)

        raw_causes = session_data.get("ranked_causes", [])
        parsed_causes: list[RankedCause] = [RankedCause(**c) if isinstance(c, dict) else c for c in raw_causes]

        return SessionState(
            session_id=session_data["session_id"],
            domain=DomainEnum(session_data.get("domain", "performance")),
            observations=parsed_obs,
            ranked_causes=parsed_causes,
            is_resolved=session_data.get("is_resolved", False),
            created_at=session_data.get("created_at", ""),
            updated_at=session_data.get("updated_at", "")
        )

    def update_session(
        self,
        session_id: str,
        observations: Dict[str, Observation],
        ranked_causes: list[RankedCause],
        is_resolved: bool = False
    ) -> Optional[SessionState]:
        """
        Updates session state with new observations and ranked causes.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        serialized_obs = {k: v.model_dump() for k, v in observations.items()}
        serialized_causes = [c.model_dump() for c in ranked_causes]

        update_payload = {
            "observations": serialized_obs,
            "ranked_causes": serialized_causes,
            "is_resolved": is_resolved,
            "updated_at": now_str
        }

        if self.client:
            try:
                self.client.table("diagnostic_sessions").update(update_payload).eq("session_id", session_id).execute()
            except Exception as e:
                logger.error(f"Supabase update failed: {e}. Updating in-memory store.")
                if session_id in _IN_MEMORY_SESSIONS:
                    _IN_MEMORY_SESSIONS[session_id].update(update_payload)
        else:
            if session_id in _IN_MEMORY_SESSIONS:
                _IN_MEMORY_SESSIONS[session_id].update(update_payload)

        return self.get_session(session_id)
