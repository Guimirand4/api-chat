# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Request
# pyrefly: ignore [missing-import]
from fastapi.responses import RedirectResponse
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

from app.config import get_settings
from app.dependencies import get_db, get_current_user
from app.schemas.user import TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()

# Configuração OAuth com Google
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google/login")
async def google_login(request: Request):
    """Redireciona o usuário para a tela de consentimento do Google."""
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Callback do Google OAuth.
    Recebe o código de autorização, troca por token, cria/busca
    o usuário e retorna um JWT.
    """
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        # pyrefly: ignore [missing-import]
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Falha ao obter dados do Google")

    auth_service = AuthService(db)
    result = auth_service.authenticate_google_user(
        google_id=user_info["sub"],
        email=user_info["email"],
        name=user_info.get("name", ""),
        picture=user_info.get("picture"),
    )

    # Redireciona para o frontend com o token
    frontend_url = settings.frontend_url
    return RedirectResponse(
        url=f"{frontend_url}/auth/callback?token={result.access_token}"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    return current_user
