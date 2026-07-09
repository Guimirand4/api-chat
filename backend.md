# Documentação das Rotas do Backend (ChatBot API)

Este documento lista todas as rotas disponíveis no backend para integração com o frontend.

> **Importante:** Todas as rotas abaixo (exceto `/health` e `/auth/google/*`) exigem autenticação. Você deve enviar o header:
> `Authorization: Bearer <seu_token_jwt>`

---

## 1. Rotas de Autenticação (`/auth`)

### `GET /auth/google/login`
Inicia o fluxo de login OAuth do Google. Redireciona o usuário para a tela de consentimento.

### `GET /auth/me`
Retorna os dados do usuário logado.
- **Header Necessário:** `Authorization: Bearer <token>`
- **Response Esperado (200 OK):**
```json
{
  "id": 1,
  "google_id": "123456789...",
  "email": "usuario@gmail.com",
  "name": "Nome do Usuário",
  "picture": "https://lh3.googleusercontent.com/a/...",
  "created_at": "2026-07-09T05:00:00Z"
}
```

---

## 2. Rotas de Histórico de Conversas (`/conversations`)

Essas rotas gerenciam os chats e histórico com a regra de limite de **no máximo 2 conversas por usuário**.

### `GET /conversations`
Retorna a lista completa do histórico de conversas (para preencher a Sidebar).
- **Response Esperado (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Nova Conversa",
    "preview": "Trecho da última mensagem...",
    "updated_at": "2026-07-09T05:00:00Z"
  }
]
```

### `POST /conversations`
Inicia um novo histórico de chat vazio.
- **Regra:** Se o usuário já possuir 2 conversas, a API retornará um erro **403 Forbidden**.
- **Response Esperado (200 OK):**
```json
{
  "id": 2,
  "title": "Nova Conversa",
  "created_at": "2026-07-09T05:10:00Z",
  "updated_at": "2026-07-09T05:10:00Z",
  "messages": []
}
```
- **Response Erro (403 Forbidden):**
```json
{
  "detail": "Limite de histórico atingido. Você só pode ter até 2 conversas ativas. Por favor, apague uma conversa antiga antes de criar uma nova."
}
```

### `GET /conversations/{id}`
Ao clicar numa conversa na sidebar, esta rota carrega todas as mensagens enviadas e recebidas.
- **Parâmetros de Rota:** `id` (ID da conversa)
- **Response Esperado (200 OK):**
```json
{
  "id": 1,
  "title": "Nova Conversa",
  "created_at": "...",
  "updated_at": "...",
  "messages": [
    {
      "id": 1,
      "conversation_id": 1,
      "sender": "user",
      "content": "Olá!",
      "created_at": "..."
    },
    {
      "id": 2,
      "conversation_id": 1,
      "sender": "bot",
      "content": "Olá, como posso ajudar?",
      "created_at": "..."
    }
  ]
}
```

### `DELETE /conversations/{id}`
Apaga uma conversa e todas as suas mensagens para liberar espaço para uma nova.
- **Parâmetros de Rota:** `id` (ID da conversa)
- **Response Esperado (200 OK):**
```json
{
  "message": "Conversa apagada com sucesso."
}
```

---

## 3. Rota de Chat com Gemini (`/conversations/{id}/messages`)

### `POST /conversations/{id}/messages`
Envia a mensagem do usuário, processa com a IA do Gemini (mantendo o contexto do histórico da conversa) e devolve a resposta gerada.
- **Parâmetros de Rota:** `id` (ID da conversa)
- **Body Request Esperado:**
```json
{
  "content": "Me fale mais sobre isso."
}
```
- **Response Esperado (200 OK) - Retorna a mensagem gerada pela IA:**
```json
{
  "id": 3,
  "conversation_id": 1,
  "sender": "bot",
  "content": "Baseado no que discutimos, aqui está a explicação...",
  "created_at": "2026-07-09T05:15:00Z"
}
```
- **Erros Possíveis:**
  - `404 Not Found` (Conversa não existe ou não pertence a este usuário)
  - `502 Bad Gateway` (Falha na comunicação com a API do Gemini)
