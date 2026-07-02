# 🤖 ChatBot API

Backend monolítico para chatbot com IA, construído com **FastAPI**, **Gemini API** e autenticação **Google OAuth 2.0**.

## 🚀 Setup

### 1. Clonar o repositório

```bash
git clone https://github.com/Guimirand4/api-chat.git
cd api-chat
```

### 2. Criar e ativar o virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

### 5. Rodar as migrations (Alembic)

```bash
alembic upgrade head
```

### 6. Iniciar o servidor

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

## 📖 Documentação

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🗂️ Estrutura do Projeto

```
app/
├── main.py           # Entry point FastAPI
├── config.py         # Configurações via .env
├── database.py       # SQLAlchemy engine + session
├── dependencies.py   # Dependencies (get_db, get_current_user)
├── models/           # Modelos SQLAlchemy
├── schemas/          # Schemas Pydantic
├── routers/          # Endpoints da API
└── services/         # Lógica de negócio
```

## 🔑 Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `GOOGLE_CLIENT_ID` | Client ID do Google OAuth |
| `GOOGLE_CLIENT_SECRET` | Client Secret do Google OAuth |
| `GEMINI_API_KEY` | API Key do Google Gemini |
| `DATABASE_URL` | URL de conexão com o banco |
| `SECRET_KEY` | Chave secreta para JWT |

## 📝 Licença

MIT
