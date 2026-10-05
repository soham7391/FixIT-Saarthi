import pytest
from app.gemini.safety import rate_limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Resets in-memory rate limiter state before each test across all backend test modules."""
    rate_limiter.reset()
