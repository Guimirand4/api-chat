from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.chat import ConversationResponse, ConversationPreview, MessageCreate, MessageResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova conversa para o usuário atual.
    Aplica a regra de limite (máx 2 conversas por usuário).
    """
    service = ChatService(db)
    return service.create_conversation(current_user.id)


@router.get("", response_model=List[ConversationPreview])
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna todo o histórico de conversas do usuário.
    Gera um preview básico para a sidebar baseado na última mensagem.
    """
    service = ChatService(db)
    conversations = service.get_user_conversations(current_user.id)
    
    # Monta os previews iterando pelas conversas
    previews = []
    for conv in conversations:
        preview_text = "Nenhuma mensagem enviada."
        if conv.messages:
            # Pega a última mensagem da conversa
            last_msg = conv.messages[-1]
            preview_text = last_msg.content[:50] + ("..." if len(last_msg.content) > 50 else "")
            
        previews.append(
            ConversationPreview(
                id=conv.id,
                title=conv.title,
                preview=preview_text,
                updated_at=conv.updated_at
            )
        )
    return previews


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Carrega uma conversa e todo seu histórico de mensagens."""
    service = ChatService(db)
    return service.get_conversation(current_user.id, conversation_id)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta uma conversa e suas mensagens em cascata."""
    service = ChatService(db)
    service.delete_conversation(current_user.id, conversation_id)
    return {"message": "Conversa apagada com sucesso."}


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recebe a mensagem do usuário, envia pro Gemini,
    e retorna a resposta do bot.
    """
    service = ChatService(db)
    # Apenas retorna a mensagem do bot como resposta primária para facilitar o front-end,
    # ou podemos retornar a lista. O front envia e recebe a resposta final.
    bot_message = service.send_message(current_user.id, conversation_id, payload.content)
    return bot_message
