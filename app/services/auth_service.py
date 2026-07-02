from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.schemas.user import TokenResponse, UserResponse

settings = get_settings()


class AuthService:
    """Serviço de autenticação — gerencia usuários e tokens JWT."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(
        self,
        google_id: str,
        email: str,
        name: str,
        picture: Optional[str] = None,
    ) -> User:
        """Busca usuário pelo google_id ou cria um novo."""
        user = self.db.query(User).filter(User.google_id == google_id).first()

        if user:
            # Atualiza dados que podem ter mudado no Google
            user.name = name
            user.email = email
            user.picture = picture
            self.db.commit()
            self.db.refresh(user)
            return user

        # Cria novo usuário
        new_user = User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def create_access_token(self, user: User) -> str:
        """Gera um JWT com dados do usuário."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def authenticate_google_user(
        self,
        google_id: str,
        email: str,
        name: str,
        picture: Optional[str] = None,
    ) -> TokenResponse:
        """Fluxo completo: busca/cria usuário e retorna token."""
        user = self.get_or_create_user(google_id, email, name, picture)
        access_token = self.create_access_token(user)

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )
