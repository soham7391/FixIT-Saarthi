from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.diagnostic import router as diagnostic_router

app = FastAPI(
    title="FixIT Saarthi Backend",
    description="AI-Assisted Computer Troubleshooting Expert System API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnostic_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FixIT Saarthi Core Engine",
        "domain": "performance"
    }
