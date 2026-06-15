# Technology Stack
> Last mapped: 2026-06-15

## Languages & Runtimes
| Language | Version | Usage |
|----------|---------|-------|
| Python | 3.12+ | Backend API, ORM, migrations |
| TypeScript | 5.x | Frontend application |
| SQL | PostgreSQL dialect | Database schema, seed data |

## Backend Framework
- **FastAPI** `0.115.6` — async-capable ASGI web framework
- **Uvicorn** `0.34.0` — ASGI server
- **Starlette** `0.41.3` — underlying ASGI toolkit

## ORM & Database
- **SQLAlchemy** (via FastAPI integration) — ORM layer
- **Alembic** — database migration management
- **PostgreSQL** — primary relational database
- Connection string: `postgresql://postgres:***@localhost:5432/ppm_platform`

## Validation & Serialization
- **Pydantic** `2.10.4` — request/response schemas with `model_config`
- **pydantic_core** `2.27.2`

## Authentication & Security
- **python-jose** — JWT encoding/decoding (imported but `SECRET_KEY`/`ALGORITHM` not configured)
- **passlib** with bcrypt — password hashing (`hash_password`, `verify_password`)

## NLP / Text Processing (installed but unused)
- **nltk** `3.9.4`
- **textblob** `0.18.0`
- **python-docx** `1.2.0`
- **lxml** `6.1.0`

## Frontend Stack
- **Next.js** `16.2.7` — React framework with App Router
- **React** `19.2.4` — UI library
- **Tailwind CSS** `4.x` — utility-first CSS
- **shadcn/ui** `4.10.0` — component library (only `Button` installed)
- **Framer Motion** `12.40.0` — animations
- **Recharts** `3.8.1` — charting library
- **Axios** `1.16.1` — HTTP client
- **Lucide React** `1.17.0` — icons

## Configuration
- **dotenv** — `.env` file loading for `DATABASE_URL`
- No `SECRET_KEY`, `ALGORITHM`, `OPENAI_API_KEY` configured yet
- `backend/app/core/config.py` exists but is **empty**

## Missing Critical Dependencies (in requirements.txt)
- `sqlalchemy` — not listed (likely in venv but not pinned)
- `alembic` — not listed
- `python-jose` — not listed
- `passlib` / `bcrypt` — not listed
- `python-dotenv` — not listed
