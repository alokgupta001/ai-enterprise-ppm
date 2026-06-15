# AI-Powered Enterprise PPM Platform

## Project Code: PPM

## Vision
An enterprise platform that helps organizations assess project management maturity, manage portfolios, evaluate risks, analyze resources, and generate AI-powered insights and recommendations.

## Status: In Development — Module 1 (Assessment Engine) ~35% complete

## Architecture

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS 4, shadcn/ui, Framer Motion, Recharts |
| Backend | FastAPI, SQLAlchemy ORM, Alembic, Pydantic v2 |
| Database | PostgreSQL 15+ |
| Authentication | JWT (python-jose), bcrypt (passlib), RBAC |
| AI Layer | OpenAI / Gemini (planned) |

### Module Roadmap
1. **Enterprise Assessment Engine** — Maturity framework, categories, questions, scoring, AI analysis
2. **Authentication & RBAC** — Register, login, JWT, role-based access
3. **AI Insights Engine** — Assessment analysis, recommendations, executive summaries
4. **Portfolio Management** — Portfolios, programs, projects, KPI tracking
5. **Risk Management** — Risks, issues, mitigation plans
6. **Resource Management** — Resources, skills, allocations, capacity planning
7. **Frontend Application** — Complete UI for all backend modules

## Conventions
- UUID primary keys for all tables
- Soft deletes via `is_deleted` flag
- UTC timestamps via `created_at` / `updated_at`
- `BaseMixin` for all ORM models
- Pydantic v2 schemas with `model_config`
- Router prefix pattern: `/api/<module>`
- Service layer for business logic (planned)

## Current Milestone: M1 — Foundation & Assessment Engine

## Brownfield Project
- Existing backend code in `backend/`
- Existing frontend scaffold in `frontend/`
- Empty directories: `ai-engine/`, `ml-engine/`, `database/schema/`, `database/seed/`
