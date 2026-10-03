from typing import Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, status
from app.schemas.diagnostic import SessionCreateRequest, SessionResponse
from app.db.supabase import SupabaseSessionManager

router = APIRouter(prefix="/api/session", tags=["Session Persistence"])
db_manager = SupabaseSessionManager()


def is_session_expired(created_at_str: str, max_age_hours: int = 24) -> bool:
    """Returns True if session created_at is older than max_age_hours."""
    if not created_at_str:
        return False
    try:
        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - created_at) > timedelta(hours=max_age_hours)
    except Exception:
        return False


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: Optional[SessionCreateRequest] = None):
    """
    Creates a new active troubleshooting session in Supabase.
    """
    try:
        domain = payload.domain if payload else SessionCreateRequest().domain
        session = db_manager.create_session(domain=domain)
        return session
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create troubleshooting session."
        )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    """
    Retrieves stored session state from Supabase by session ID.
    Returns HTTP 404 if missing or invalid.
    Returns HTTP 410 if session is older than 24 hours.
    """
    if not session_id or not session_id.strip():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session ID cannot be empty."
        )
    try:
        session = db_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found."
            )
        if is_session_expired(session.created_at, max_age_hours=24):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Troubleshooting session has expired (sessions expire after 24 hours)."
            )
        return session
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session details."
        )
