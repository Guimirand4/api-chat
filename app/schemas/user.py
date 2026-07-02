from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    """Schema para criação de usuário (dados vindos do Google)."""

    google_id: str
    email: str
    name: str
    picture: Optional[str] = None


class UserResponse(BaseModel):
    """Schema de resposta com dados do usuário."""

    id: int
    google_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema de resposta com token JWT."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
