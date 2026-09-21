import base64
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status, Request
from app.schemas.diagnostic import (
    DiagnosticRequest,
    DiagnosticResponse,
    Observation,
    TextParseRequest,
    DomainEnum
)
from app.gemini.client import GeminiAssistant
from app.expert_engine.evaluator import ExpertEvaluator
from app.expert_engine.ranker import CauseRanker
from app.db.supabase import SupabaseSessionManager

router = APIRouter(prefix="/api/diagnostic", tags=["Diagnostic Engine"])

gemini_assistant = GeminiAssistant()
evaluator = ExpertEvaluator(domain=DomainEnum.PERFORMANCE)
ranker = CauseRanker()
db_manager = SupabaseSessionManager()


@router.post("/parse-text", response_model=List[Observation])
def parse_text(payload: TextParseRequest, request: Request):
    """
    Submits user text problem statement to AI Assistance Layer.
    Extracts validated structured observations compatible with the Observation schema.
    Enforces input safety, prompt injection resistance, scope guarding, and rate limits.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    text = payload.get_text()

    try:
        observations = gemini_assistant.parse_problem_text(text, client_ip=client_ip)
        return observations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse text: {str(e)}"
        )


@router.post("/parse-screenshot", response_model=List[Observation])
async def parse_screenshot(request: Request):
    """
    Submits Task Manager screenshot image to AI Assistance Layer.
    Accepts multipart file upload or JSON payload containing screenshot_base64.
    Extracts relevant CPU, RAM, Disk, and top_process_name observations.
    Enforces size limits (<= 5 MB), single file restriction, image format verification, and rate limits.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    image_bytes = b""
    content_type = request.headers.get("content-type", "")
    file_count = 1
    extracted_mime = "image/png"

    if "multipart/form-data" in content_type:
        form = await request.form()
        files = form.getlist("file")
        file_count = len(files)
        if file_count > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only one screenshot per request is allowed."
            )
        file_obj = files[0] if files else None
        if file_obj and hasattr(file_obj, "read"):
            image_bytes = await file_obj.read()
            if hasattr(file_obj, "content_type") and file_obj.content_type:
                extracted_mime = file_obj.content_type
    else:
        try:
            body = await request.json()
            b64_str = body.get("screenshot_base64", "")
            if b64_str:
                b64_clean = b64_str.split(",")[-1]
                try:
                    image_bytes = base64.b64decode(b64_clean)
                except Exception:
                    image_bytes = b64_clean.encode('utf-8')
        except Exception:
            pass

    try:
        observations = gemini_assistant.parse_task_manager_screenshot(
            image_bytes=image_bytes,
            client_ip=client_ip,
            content_type=extracted_mime,
            file_count=file_count
        )
        return observations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse screenshot: {str(e)}"
        )


@router.post("/evaluate", response_model=DiagnosticResponse)
def evaluate_diagnostic(request: DiagnosticRequest, http_req: Request):
    """
    Core diagnostic evaluation endpoint connected to Supabase session persistence:
    1. If session_id is provided, fetches session state from Supabase (returns 404 if invalid/missing).
    2. Merges existing session observations with Gemini text/screenshot extractions and request observations.
    3. Evaluates observations through the deterministic Expert Engine.
    4. Persists updated observations, ranked causes, and timestamps in Supabase troubleshooting_sessions table.
    5. Returns expert engine diagnostic response.
    """
    client_ip = http_req.client.host if http_req.client else "127.0.0.1"
    accumulated_obs: Dict[str, Observation] = {}
    existing_session = None

    if request.session_id:
        existing_session = db_manager.get_session(request.session_id)
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found."
            )
        for obs in existing_session.observations:
            accumulated_obs[obs.key] = obs

    if request.text_input and request.text_input.strip():
        try:
            text_obs = gemini_assistant.parse_problem_text(
                request.text_input,
                client_ip=client_ip,
                session_id=request.session_id
            )
            for obs in text_obs:
                accumulated_obs[obs.key] = obs
        except HTTPException:
            raise
        except Exception:
            pass

    if request.screenshot_base64 and request.screenshot_base64.strip():
        try:
            b64_clean = request.screenshot_base64.split(",")[-1]
            try:
                img_bytes = base64.b64decode(b64_clean)
            except Exception:
                img_bytes = b64_clean.encode('utf-8')
            img_obs = gemini_assistant.parse_task_manager_screenshot(
                img_bytes,
                client_ip=client_ip,
                session_id=request.session_id
            )
            for obs in img_obs:
                accumulated_obs[obs.key] = obs
        except HTTPException:
            raise
        except Exception:
            pass

    for obs in request.observations:
        accumulated_obs[obs.key] = obs

    if request.top_process_name and "top_process_name" not in accumulated_obs:
        accumulated_obs["top_process_name"] = Observation(key="top_process_name", value=request.top_process_name)

    obs_list = list(accumulated_obs.values())

    raw_evaluations = evaluator.evaluate(obs_list)
    ranked_causes = ranker.rank_causes(raw_evaluations, accumulated_obs)

    # Persist in Supabase if session_id is present
    if request.session_id:
        db_manager.update_session(
            session_id=request.session_id,
            observations=obs_list,
            ranked_causes=ranked_causes,
            status="in_progress"
        )

    return DiagnosticResponse(
        session_id=request.session_id,
        domain=request.domain,
        processed_observations=obs_list,
        ranked_causes=ranked_causes,
        status="completed"
    )
