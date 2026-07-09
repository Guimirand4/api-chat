from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router

__all__ = ["health_router", "auth_router", "chat_router"]
