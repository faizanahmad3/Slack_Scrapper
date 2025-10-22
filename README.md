# Slack Knowledge Q&A System

A production-ready FastAPI application that ingests Slack channel messages, creates embeddings using LangChain, stores them in Qdrant vector database, and provides intelligent Q&A capabilities with incremental updates.

## 🌟 Features

- **Smart Incremental Ingestion**: Only processes new messages since last run, saving API costs and time
- **Dynamic LLM/Embedding Providers**: Pluggable architecture supporting multiple LLM providers (OpenAI by default)
- **Vector Search**: Qdrant-powered semantic search for accurate context retrieval
- **Per-Channel Collections**: Isolated vector stores for each Slack channel
- **Comprehensive Logging**: Detailed logs with line numbers showing exactly what's being processed
- **RESTful API**: Clean FastAPI endpoints with Pydantic validation
- **Metadata Tracking**: Persistent state management for incremental updates

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [How It Works](#how-it-works)
- [Adding New Providers](#adding-new-providers)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│   Slack     │─────▶│   Ingestion  │─────▶│  Embeddings │─────▶│  Qdrant  │
│   Channel   │      │   Pipeline   │      │  (OpenAI)   │      │  Vector  │
└─────────────┘      └──────────────┘      └─────────────┘      │   Store  │
                            │                                     └──────────┘
                            │                                           │
                            ▼                                           │
                     ┌──────────────┐                                  │
                     │   Metadata   │                                  │
                     │   Storage    │                                  │
                     │  (JSON File) │                                  │
                     └──────────────┘                                  │
                                                                        │
┌─────────────┐      ┌──────────────┐      ┌─────────────┐           │
│    User     │─────▶│      QA      │─────▶│     LLM     │◀──────────┘
│    Query    │      │   Pipeline   │      │  (OpenAI)   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Response   │
                     │ with Sources │
                     └──────────────┘
```

---

## 📁 Project Structure

```
slack_scrapper/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Pydantic settings with env support
│   ├── logging_config.py            # Centralized logging setup
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic models (request/response)
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── slack_client.py          # Slack API wrapper
│   │
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── ingest.py                # Ingestion pipeline with incremental updates
│   │   └── qa.py                    # Q&A pipeline with RAG
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   └── clean.py                 # Message cleaning and structuring
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                  # Provider interfaces
│   │   ├── openai_embeddings.py     # OpenAI embeddings implementation
│   │   ├── openai_llm.py            # OpenAI chat LLM implementation
│   │   └── registry.py              # Provider factory
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── metadata.py              # Ingestion metadata tracking
│   │
│   └── vectorstore/
│       ├── __init__.py
│       └── qdrant_store.py          # Qdrant wrapper
│
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (create from .env.example)
├── .env.example                     # Environment template
├── ingestion_metadata.json          # Auto-generated: tracks ingestion state
└── README.md                        # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- Qdrant (running locally or remote)
- Slack Bot Token with appropriate scopes
- OpenAI API Key (or other LLM provider)

### Setup Steps

1. **Clone and Navigate**
```bash
cd /path/to/slack_scrapper
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Qdrant (Local)**
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

5. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

6. **Run Application**
```bash
uvicorn main:app --reload
# Or: python main.py
```

Server will start at `http://0.0.0.0:8000`

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Provider Selection
EMBEDDING_PROVIDER=openai                    # Embedding provider (openai)
EMBEDDING_MODEL=text-embedding-3-small       # Embedding model
LLM_PROVIDER=openai                          # LLM provider (openai)
LLM_MODEL=gpt-4o-mini                        # Chat model (gpt-4o, gpt-4o-mini, etc.)

# API Keys
OPENAI_API_KEY=sk-...                        # Your OpenAI API key
SLACK_BOT_TOKEN=xoxb-...                     # Your Slack Bot User OAuth Token

# Qdrant Configuration
QDRANT_URL=http://localhost                  # Qdrant host
QDRANT_PORT=6333                             # Qdrant port

# Ingestion Settings (Optional)
MAX_MESSAGES_PER_CHANNEL=                    # Limit messages (empty = unlimited)
```

### Slack Bot Setup

1. **Create Slack App**: https://api.slack.com/apps
2. **Add Bot User**: Features → App Home → Add Bot User
3. **Add Scopes** (OAuth & Permissions → Bot Token Scopes):
   - `channels:read` - View basic channel info
   - `channels:history` - View messages in public channels
   - `groups:read` - View basic private channel info
   - `groups:history` - View messages in private channels
4. **Install to Workspace**: OAuth & Permissions → Install to Workspace
5. **Copy Token**: Bot User OAuth Token (starts with `xoxb-`)
6. **Invite Bot**: In Slack channel, run `/invite @YourBotName`

---

## 🔌 API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. List Channels

**Endpoint:** `GET /channels`

**Description:** Get list of all Slack channels the bot has access to

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_private` | boolean | `true` | Include private channels |

**Request:**
```bash
curl "http://localhost:8000/channels?include_private=true"
```

**Response:**
```json
{
  "channels": [
    "general",
    "random",
    "engineering",
    "product-updates"
  ]
}
```

---

### 3. Question & Answer (Main Endpoint)

**Endpoint:** `POST /qa`

**Description:** Ask questions about Slack channel content with optional ingestion

**Request Body:**
```json
{
  "channel": "string",              // Required: Channel name (without #)
  "query": "string",                // Required: Your question
  "top_k": 5,                       // Optional: Number of context chunks (1-20)
  "refresh": false,                 // Optional: Ingest new messages before answering
  "force_full_refresh": false       // Optional: Re-ingest entire channel (requires refresh=true)
}
```

**Response:**
```json
{
  "answer": "string",               // Generated answer from LLM
  "sources": [                      // Source documents used
    {
      "text": "string",             // Message content
      "metadata": {
        "channel": "string",        // Channel name
        "ts": "string",             // Slack timestamp
        "datetime": "string",       // ISO datetime
        "user": "string",           // User ID
        "_id": "string",            // Document ID in Qdrant
        "_collection_name": "string" // Qdrant collection
      }
    }
  ]
}
```

**Example Requests:**

#### A. First-time Ingestion + Query
```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "engineering",
    "query": "What was deployed last week?",
    "top_k": 5,
    "refresh": true
  }'
```

#### B. Query Without Re-ingestion
```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "engineering",
    "query": "Any bugs reported?",
    "top_k": 3,
    "refresh": false
  }'
```

#### C. Incremental Update + Query
```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "engineering",
    "query": "What are the latest updates?",
    "refresh": true
  }'
```
*This will only ingest NEW messages since last run*

#### D. Force Full Re-ingestion
```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "engineering",
    "query": "Summarize everything",
    "refresh": true,
    "force_full_refresh": true
  }'
```
*This will re-process ALL messages in the channel*

**Example Response:**
```json
{
  "answer": "Last week, the team deployed the new authentication service using OAuth2. The deployment was successful and went live on Tuesday at 3 PM.",
  "sources": [
    {
      "text": "We successfully deployed the new auth service with OAuth2 integration",
      "metadata": {
        "channel": "engineering",
        "ts": "1760550885.336289",
        "datetime": "2025-10-15T22:54:45.336289",
        "user": "U09MJQBCGV6",
        "_id": "abc123",
        "_collection_name": "engineering"
      }
    },
    {
      "text": "Deployment went smoothly, no issues reported",
      "metadata": {
        "channel": "engineering",
        "ts": "1760551000.445566",
        "datetime": "2025-10-15T22:56:40.445566",
        "user": "U09MJQBCGV6",
        "_id": "def456",
        "_collection_name": "engineering"
      }
    }
  ]
}
```

---

### 4. Channel Statistics

**Endpoint:** `GET /channels/{channel}/stats`

**Description:** Get ingestion statistics for a specific channel

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | string | Channel name |

**Request:**
```bash
curl http://localhost:8000/channels/engineering/stats
```

**Response:**
```json
{
  "channel": "engineering",
  "last_timestamp": "1760562526.888459",
  "total_messages": 1247,
  "last_updated": "1760562526"
}
```

**Fields:**
- `last_timestamp`: Last processed message timestamp (Slack format)
- `total_messages`: Total number of messages ingested so far
- `last_updated`: Unix timestamp of last ingestion

---

## 💡 Usage Examples

### Workflow 1: First-Time Setup

```bash
# 1. Check if API is running
curl http://localhost:8000/health

# 2. List available channels
curl http://localhost:8000/channels

# 3. First ingestion of a channel
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "general",
    "query": "What topics have been discussed?",
    "refresh": true
  }'
```

### Workflow 2: Daily Updates

```bash
# Incremental update - only new messages are processed
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "general",
    "query": "What are the latest updates?",
    "refresh": true
  }'
```

### Workflow 3: Check Stats

```bash
# See how many messages have been ingested
curl http://localhost:8000/channels/general/stats
```

---

## 🔄 How It Works

### Incremental Ingestion

The system uses smart incremental updates to avoid re-processing messages:

1. **First Run** (`refresh=true`):
   - Fetches ALL messages from Slack
   - Creates embeddings for each message
   - Stores in Qdrant collection named after channel
   - Saves latest message timestamp to `ingestion_metadata.json`

2. **Subsequent Runs** (`refresh=true`):
   - Reads last processed timestamp from metadata
   - Fetches ONLY messages newer than that timestamp
   - Creates embeddings for new messages only
   - Appends to existing Qdrant collection
   - Updates metadata with new latest timestamp

3. **Query Without Refresh** (`refresh=false`):
   - Skips ingestion entirely
   - Directly queries existing Qdrant collection
   - Fast response, no API costs

4. **Force Full Refresh** (`refresh=true, force_full_refresh=true`):
   - Re-processes entire channel history
   - Useful if you need to rebuild the index

### Message Processing Pipeline

```
Slack Messages
    ↓
[Clean & Structure]
    ↓
Remove Slack formatting (<@USER>, <#CHANNEL>, URLs)
Add metadata (timestamp, user, channel)
    ↓
[Create Embeddings]
    ↓
Convert to vector using OpenAI text-embedding-3-small
    ↓
[Store in Qdrant]
    ↓
Save to collection named after channel
    ↓
[Update Metadata]
    ↓
Track last processed timestamp
```

### Query Pipeline (RAG)

```
User Query
    ↓
[Embed Query]
    ↓
Convert to vector
    ↓
[Vector Search]
    ↓
Retrieve top_k similar messages from Qdrant
    ↓
[Format Context]
    ↓
Combine retrieved messages into context
    ↓
[LLM Generation]
    ↓
Send context + query to GPT-4o
    ↓
[Return Answer + Sources]
```

---

## 🧩 Adding New Providers

The system is designed to support multiple LLM/embedding providers. Here's how to add a new one:

### 1. Create Provider Implementation

**Example: Adding Anthropic Claude**

```python
# app/providers/anthropic_llm.py
from langchain_anthropic import ChatAnthropic
from app.config import Settings
from app.providers.base import LLMProvider

class AnthropicChatProvider(LLMProvider):
    def create(self, settings: Settings) -> ChatAnthropic:
        return ChatAnthropic(
            model=settings.llm_model,
            anthropic_api_key=settings.anthropic_api_key,
        )
```

### 2. Register Provider

```python
# app/providers/registry.py
from app.providers.anthropic_llm import AnthropicChatProvider

LLM_PROVIDERS: Dict[str, LLMProvider] = {
    "openai": OpenAIChatProvider(),
    "anthropic": AnthropicChatProvider(),  # Add this
}
```

### 3. Update Configuration

```python
# app/config.py
class Settings(BaseSettings):
    # ... existing fields ...
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
```

### 4. Use New Provider

```bash
# .env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

Same process applies for embedding providers!

---

### Viewing Detailed Logs

Logs show:
- **Line numbers** for easy debugging
- **Exact messages** being ingested
- **Timestamps** for tracking
- **API calls** and responses

Example:
```
2025-10-22 02:17:10 - app.pipelines.ingest:53 - INFO - ========== INGESTING 2 NEW MESSAGES ==========
2025-10-22 02:17:10 - app.pipelines.ingest:59 - INFO -   [1] ts=1760562700.123456, user=U09MJQBCGV6, text='New deployment completed'
2025-10-22 02:17:10 - app.pipelines.ingest:59 - INFO -   [2] ts=1760562800.234567, user=U09LMEQDQ3X, text='All tests passing'
```

---

## 📊 Performance Tips

1. **Use Incremental Updates**: Always use `refresh=true` without `force_full_refresh` for daily updates
2. **Adjust top_k**: Lower `top_k` values (3-5) are faster and often sufficient
3. **Set MAX_MESSAGES_PER_CHANNEL**: Limit for very large channels during first ingestion
4. **Use refresh=false**: When asking multiple questions, only refresh once

---

## 🔐 Security Notes

- Never commit `.env` file to version control
- Rotate API keys periodically
- Use environment-specific tokens (dev/staging/prod)
- Limit Slack bot scopes to minimum required
- Run Qdrant with authentication in production

---

**Built with using FastAPI, LangChain, Qdrant, and OpenAI**

## DEMO RUN RESULTS

- Please see the snapshots below for DEMO run results. I setup a chaneel in my personal slack. I didn't do it on intuit channels as I was facing SSL certificate error while making connection to it. Also I didn't had LLM API key and had to go through some blockers on dev portal to get that. To accelerate the development, I used my personal slack and a demo open AI api key. The only change a person needs to make is add slack key and llm api key in env file. 

![Pasted image.png](Pasted%20image.png)
![Pasted image 1.png](Pasted%20image%201.png)
![Pasted image 2.png](Pasted%20image%202.png)
![Screenshot from 2025-10-22 12-59-56.png](Screenshot%20from%202025-10-22%2012-59-56.png)
![Screenshot from 2025-10-22 13-00-38.png](Screenshot%20from%202025-10-22%2013-00-38.png)