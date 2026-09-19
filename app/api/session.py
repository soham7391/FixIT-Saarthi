from typing import Optional
from fastapi import APIRouter, HTTPException, status
from app.schemas.diagnostic import SessionCreateRequest, SessionResponse
from app.db.supabase import SupabaseSessionManager

router = APIRouter(prefix="/api/session", tags=["Session Persistence"])
db_manager = SupabaseSessionManager()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: Optional[SessionCreateRequest] = None):
    """
    Creates a new active troubleshooting session in Supabase.
    """
    try:
        domain = payload.domain if payload else SessionCreateRequest().domain
        session = db_manager.create_session(domain=domain)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create troubleshooting session."
        )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    """
    Retrieves stored session state from Supabase by session ID.
    Returns HTTP 404 if missing or invalid.
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
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session details."
        )
