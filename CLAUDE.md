# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Alpha Genie is an AI-powered asset management platform for investment teams. It provides document analysis with LLMs, a market data dashboard, portfolio analytics, and an AI assistant with tool-calling capabilities.

## Development Commands

```bash
# Install all dependencies
make install

# Run both backend and frontend concurrently
make dev

# Run individually
make backend     # FastAPI on port 8000
make frontend    # Next.js on port 3000

# Tests
make test
cd backend && . venv/bin/activate && pytest           # backend only
cd backend && . venv/bin/activate && pytest path/to/test_file.py::test_name  # single test
cd frontend && npm test                               # frontend only

# Cleanup
make clean
```

## Architecture

Monorepo with a **Next.js 16 frontend** and **Python FastAPI backend**, deployed separately on Railway via nixpacks.

### Backend (`/backend/`)

Entry point: `app/main.py` — FastAPI app with CORS, router registration, and `init_db()` on startup.

**Layer structure:**
- `app/api/` — Route handlers (`agent.py`, `market.py`, `documents.py`, `portfolio.py`, `earnings.py`, `chat.py`)
- `app/agents/` — AI agent layer:
  - `assistant.py` — Main LangChain agent executor (OpenAI tools agent with automatic tool calling)
  - `tools.py` — LangChain tools: `get_stock_price` (yfinance), `get_earnings_sentiment`, `get_assetmanagement_web_search` (Tavily)
  - `llm.py` — `LLMService` singleton supporting OpenAI and Anthropic; handles summarization, QA, sentiment analysis
  - `rag/` — RAG pipeline (vectorstore/retriever/ingest — partially implemented)
- `app/services/` — Business logic (`market_data.py` uses asyncio for parallel Yahoo Finance fetching, `document.py` for PDF/DOCX/TXT parsing, `earning_call_transcript.py`)
- `app/models/` — SQLAlchemy ORM models (`Document`, `Portfolio`, `Holding`, `User`)
- `app/core/` — `config.py` (Pydantic settings) and `database.py` (SQLAlchemy setup, SQLite dev / PostgreSQL prod)

API docs available at `http://localhost:8000/docs`.

### Frontend (`/frontend/`)

Entry point: `src/app/layout.tsx` — Root layout with three-column structure: `Sidebar` + main content + `ChatPanel`.

**Key structure:**
- `src/app/` — Pages: dashboard (`page.tsx`), `documents/`, `market/`, `portfolio/`
- `src/components/` — `Sidebar.tsx` (navigation), `ChatPanel.tsx` (AI assistant chat panel, right side)
- `src/lib/api.ts` — Fetch wrapper with `get`, `post`, `put`, `delete`, `uploadFile` methods

**UI stack:** Tailwind CSS (dark theme: `#0a0a0f` / `#0d0d14` / `#1a1a24`), Tremor (charts/dashboards), Headless UI, Recharts.

TypeScript path alias: `@/*` → `./src/*`.

### Data Flow

Frontend `ChatPanel` → `POST /api/agent/assistant` → `assistant.py` agent executor → tools (stock price / earnings / web search) → LangChain response → streamed back to UI.

Document uploads → `POST /api/documents/upload` → PDF/DOCX/TXT extraction → LLM summarization → stored in SQLite with file path in `data/uploads/`.

Market data → `GET /api/market/*` → `market_data.py` (yfinance, async parallel fetching) → JSON response.

### Database

SQLite at `data/alpha_genie.db` (local); PostgreSQL in production. Tables auto-created on startup. No migrations tool — schema changes require dropping and recreating tables in development.

## Environment Variables

Backend (`.env` in `/backend/`):
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` — LLM providers
- `TAVILY_API_KEY` — Web search tool used by the agent
- `LANGSMITH_API_KEY` — LangSmith observability (optional)
- `NEWS_API_KEY`, `FMP_API_KEY`, `EARNINGS_API_KEY` — Financial data providers
- `DATABASE_URL` — Defaults to SQLite; set PostgreSQL URL for prod
- `SECRET_KEY` — JWT secret

Frontend (`.env.local` in `/frontend/`):
- `NEXT_PUBLIC_API_URL` — Backend URL (default: `http://localhost:8000`)

## Deployment

Both services deploy to Railway using `nixpacks.toml` files. Backend runs `uvicorn app.main:app` on `$PORT`; frontend runs `npm run build && npm start`. CORS is configured with wildcard (`*`) for Railway compatibility.
