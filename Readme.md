# AI-Powered Enterprise PPM Platform

An AI-integrated platform for project portfolio management — assess PMO maturity, diagnose project health, and query data using natural language.

## Tech Stack

**Backend:** FastAPI · SQLAlchemy · PostgreSQL · LangChain · OpenAI (GPT-4o-mini)  
**Frontend:** Next.js 16 · React 19 · TypeScript · Tailwind CSS · Recharts  
**Auth:** JWT · bcrypt · Google OAuth

## Features

- **Maturity Assessment** — 25 questions across 5 PMO categories with AI-scored text responses and radar chart results
- **AI Assistant** — Multi-agent chat (Risk, Resource, Timeline agents) with SSE streaming
- **Root Cause Analysis** — Automated diagnosis of delayed/at-risk projects
- **NL-to-SQL** — Natural language database queries with SQL injection protection
- **Auth & Multi-Tenancy** — JWT login, Google OAuth, organization-scoped data isolation

> All AI features have rule-based fallbacks and work without an OpenAI API key.

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ppm_platform
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...       # optional
```

```bash
alembic upgrade head         # run migrations
python -m app.seed           # seed sample data
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Default Login

```
Email: admin@acme.com
Password: password123
```

## API Endpoints

| Group | Prefix | Key Routes |
|---|---|---|
| Auth | `/api/auth` | `POST /register`, `POST /login`, `GET /me` |
| Assessments | `/api/assessments` | `GET /frameworks`, `POST /start`, `POST /{id}/submit`, `GET /{id}/results` |
| Projects | `/api/projects` | `GET /`, `GET /{id}/summary` |
| Assistant | `/api/assistant` | `POST /chat/stream`, `GET /conversations` |

Swagger docs available at `http://localhost:8000/docs`

## Project Structure

```
backend/
  app/
    routers/       # API endpoints
    models/        # SQLAlchemy ORM (11 tables)
    services/      # AI evaluator, scoring, root cause, NL-to-SQL
    agents/        # Risk, Resource, Timeline specialist agents
    core/          # Auth, config, security

frontend/
  app/
    login/         # Auth pages
    assessments/   # Maturity assessment flow
    assistant/     # AI chat interface
  components/      # Navbar, UI components
  lib/             # API client, utilities
```

## License

Educational and enterprise evaluation purposes.