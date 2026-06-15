# Architecture
> Last mapped: 2026-06-15

## Pattern: Layered Monolith (FastAPI)

```
┌─────────────────────────────────────────────┐
│                  Frontend                    │
│           Next.js 16 + Tailwind              │
│              (Port 3000)                     │
├─────────────────────────────────────────────┤
│                Backend API                   │
│             FastAPI + Uvicorn                 │
│              (Port 8000)                     │
├──────────┬──────────┬───────────────────────┤
│ Routers  │ Schemas  │ Services (planned)     │
├──────────┴──────────┴───────────────────────┤
│              SQLAlchemy ORM                  │
│            Models + BaseMixin                │
├─────────────────────────────────────────────┤
│          PostgreSQL Database                 │
│     Alembic Migrations + Seed Data           │
└─────────────────────────────────────────────┘
```

## Layers

### 1. Router Layer (`backend/app/routers/`)
- Receives HTTP requests
- Validates input via Pydantic schemas
- Calls service layer (or directly queries DB — current state)
- Returns Pydantic response models
- Files: `organization.py`, `assessment.py`

### 2. Schema Layer (`backend/app/schemas/`)
- Pydantic v2 `BaseModel` classes
- Separate `Create` and `Response` schemas
- Uses `model_config = {"from_attributes": True}` for ORM compatibility
- Files: `organization.py`, `assessment.py`, `auth.py`

### 3. Service Layer (`backend/app/services/`)
- **Planned but empty** — `assessment_service.py` exists with no content
- Should contain business logic separated from routes

### 4. Model Layer (`backend/app/models/`)
- SQLAlchemy ORM models inheriting from `Base` + `BaseMixin`
- `BaseMixin` provides: `id` (UUID), `created_at`, `updated_at`, `is_deleted`
- Files: `base.py`, `enums.py`, `organization.py`, `user.py`, `assessment.py`

### 5. Core Layer (`backend/app/core/`)
- `security.py` — bcrypt password hashing/verification
- `auth.py` — JWT token creation (imports from empty `config.py`)
- `config.py` — **empty file** (missing `SECRET_KEY`, `ALGORITHM`)

### 6. Database Layer (`backend/app/database.py`)
- `engine` — SQLAlchemy engine from `DATABASE_URL` env var
- `SessionLocal` — session factory
- `get_db()` — FastAPI dependency for DB sessions
- `Base` — declarative base for all models

## Entry Points
- **Backend**: `backend/app/main.py` — FastAPI app with CORS, router registration, startup table creation
- **Frontend**: `frontend/app/page.tsx` — default Next.js boilerplate (unchanged)

## Data Flow (Current)
```
HTTP Request → FastAPI Router → Pydantic Schema Validation → Direct DB Query → Pydantic Response
```

## Data Flow (Target)
```
HTTP Request → Router → Schema Validation → Service Layer → Repository Layer → DB → Response
```

## Unimplemented Layers
- **Repository Layer** — no repository pattern
- **Middleware** — no auth middleware, no request logging
- **Error Handling** — no global exception handler
- **AI Engine** — `ai-engine/` directory is empty
- **ML Engine** — `ml-engine/` directory is empty
