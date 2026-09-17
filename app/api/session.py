from fastapi import APIRouter, HTTPException, status
from app.schemas.diagnostic import SessionCreate, SessionState
from app.db.supabase import SupabaseSessionManager

router = APIRouter(prefix="/api/session", tags=["Session"])
db_manager = SupabaseSessionManager()


@router.post("", response_model=SessionState, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate):
    """
    Creates a new troubleshooting session.
    """
    try:
        session = db_manager.create_session(domain=payload.domain)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/{session_id}", response_model=SessionState)
def get_session(session_id: str):
    """
    Retrieves state and history of an existing diagnostic session.
    """
    session = db_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{session_id}' not found."
        )
    return session
