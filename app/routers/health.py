# pyrefly: ignore [missing-import]
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Verifica se a API está online."""
    return {
        "status": "healthy",
        "message": "API is running 🚀",
    }
