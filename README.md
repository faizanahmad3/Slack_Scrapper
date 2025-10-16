# Slack Knowledge Q&A (FastAPI + LangChain + Qdrant)

Modular Slack ingestion, cleaning, embedding, and Q&A pipeline using LangChain, OpenAI (default, pluggable), and Qdrant (local) vector database.

## Features
- Ingest Slack channel messages, clean and structure them
- Dynamic embedding and LLM providers (OpenAI by default)
- Qdrant vector database (collections per Slack channel name)
- FastAPI endpoint for channel-specific Q&A
- Modular, extensible components

## Requirements
- Python 3.10+
- Local Qdrant running (default `http://localhost:6333`)
- Slack Bot Token with `conversations:read` scope
- OpenAI API key (default provider)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your keys and settings.

## Run API
```bash
uvicorn app.main:app --reload
```

## Example Request
POST `/qa`
```json
{
  "channel": "general",
  "query": "What did we decide about the release?",
  "refresh": false
}
```

## Switch Providers
Set in `.env`:
- `EMBEDDING_PROVIDER` (e.g. `openai`)
- `EMBEDDING_MODEL` (e.g. `text-embedding-3-small`)
- `LLM_PROVIDER` (e.g. `openai`)
- `LLM_MODEL` (e.g. `gpt-4o-mini`)

Add new providers by implementing the base interfaces in `app/providers` and registering them in the provider factory.
