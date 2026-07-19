from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from app.config import get_settings
from app.models.chat import Conversation, Message

settings = get_settings()

class ChatService:
    """Serviço para gerenciamento de chats, limites e integração com Gemini."""

    def __init__(self, db: Session):
        self.db = db
        # Inicializa o client da nova biblioteca google-genai
        self.ai_client = genai.Client(api_key=settings.gemini_api_key)

    def create_conversation(self, user_id: int, title: str = "Nova Conversa") -> Conversation:
        """Cria uma nova conversa, respeitando o limite de 2 conversas por usuário."""
        # 1. Verificar o limite de conversas
        count = self.db.query(Conversation).filter(Conversation.user_id == user_id).count()
        if count >= 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Limite de histórico atingido. Você só pode ter até 2 conversas ativas. Por favor, apague uma conversa antiga antes de criar uma nova."
            )

        # 2. Criar a conversa
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_user_conversations(self, user_id: int) -> List[Conversation]:
        """Retorna todas as conversas do usuário ordenadas pela data de atualização."""
        return self.db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.updated_at.desc())\
            .all()

    def get_conversation(self, user_id: int, conversation_id: int) -> Conversation:
        """Busca uma conversa específica do usuário. Se não existir ou for de outro, retorna 404."""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada.")
        return conversation

    def delete_conversation(self, user_id: int, conversation_id: int):
        """Apaga uma conversa do usuário."""
        conversation = self.get_conversation(user_id, conversation_id)
        self.db.delete(conversation)
        self.db.commit()

    def send_message(self, user_id: int, conversation_id: int, content: str) -> Message:
        """
        Salva a mensagem do usuário, envia o histórico para a Gemini API,
        recebe a resposta e salva a mensagem da IA.
        """
        # 1. Valida a conversa e recupera o histórico atual
        conversation = self.get_conversation(user_id, conversation_id)

        # 2. Prepara o histórico para o formato do google-genai
        history_contents = []
        for msg in conversation.messages:
            # O sender deve ser mapeado: 'user' -> 'user', 'bot' -> 'model'
            role = "user" if msg.sender == "user" else "model"
            history_contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
            )

        # 3. Salva a nova mensagem do usuário no banco
        user_message = Message(
            conversation_id=conversation.id,
            sender="user",
            content=content
        )
        self.db.add(user_message)
        self.db.commit()
        
        # Obtém a data e hora atual
        from datetime import datetime
        current_date = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        
        # 4. Envia a mensagem via Gemini mantendo o contexto (historico)
        try:
            chat_session = self.ai_client.chats.create(
                model="gemini-2.5-flash",
                history=history_contents,
                config=types.GenerateContentConfig(
                    system_instruction=f"A data e hora atual é {current_date}."
                )
            )
            response = chat_session.send_message(content)
            bot_reply = response.text
        except Exception as e:
            # Em caso de erro na IA, tentamos desfazer a adição da mensagem do usuário ou
            # mantemos, mas aqui é melhor reportar erro para o front.
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erro de comunicação com a IA: {str(e)}"
            )

        # 5. Salva a resposta do bot
        bot_message = Message(
            conversation_id=conversation.id,
            sender="bot",
            content=bot_reply
        )
        self.db.add(bot_message)
        
        # Atualiza a data de 'updated_at' da conversa
        # SQLAlchemy faz isso automaticamente se mudarmos algum dado,
        # mas forçar um commit com as novas mensagens já atua no relacionamento.
        self.db.commit()
        self.db.refresh(bot_message)

        return bot_message
