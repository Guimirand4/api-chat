from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    """Schema para o envio de uma mensagem do usuário."""
    content: str


class MessageResponse(BaseModel):
    """Schema de resposta para uma mensagem."""
    id: int
    conversation_id: int
    sender: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """Schema de resposta para uma conversa com suas mensagens."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationPreview(BaseModel):
    """Schema para listagem de histórico na sidebar."""
    id: int
    title: str
    preview: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
