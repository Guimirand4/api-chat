from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import health_router, auth_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de startup e shutdown da aplicação."""
    # Startup: cria as tabelas no banco (apenas dev, em prod usar Alembic)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # Em ambientes serverless (Vercel) o filesystem é read-only
        pass
    yield
    # Shutdown: cleanup se necessário


app = FastAPI(
    title=settings.app_name,
    description="API backend para chatbot com IA (Gemini) e autenticação Google",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware de sessão (necessário para OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# CORS — permite requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(health_router)
app.include_router(auth_router)
