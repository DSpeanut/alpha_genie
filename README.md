# Alpha Genie

AI-powered asset management platform for investment teams.

## Features (MVP)
- Document Analysis with LLM
- Market Data Dashboard
- Portfolio Analytics

## Tech Stack
- **Frontend:** Next.js + Tremor
- **Backend:** Python FastAPI
- **Database:** SQLite (local) / PostgreSQL (production)
- **LLM:** OpenAI / Claude / Ollama

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
```
alpha_genie/
├── frontend/          # Next.js application
├── backend/           # Python FastAPI
├── data/              # Local storage
├── notebooks/         # Research notebooks
└── README.md
```
