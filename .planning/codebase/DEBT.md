# Codebase Mapping — Technical Debt
> Last mapped: 2026-06-15

## Identified Technical Debt & Code Issues

### Empty Source Files
- `backend/app/core/config.py` is empty (causes import failures in `auth.py`).
- `backend/app/services/assessment_service.py` is empty.

### DB Connection & Migrations
- `startup` function in `main.py` uses `Base.metadata.create_all(bind=engine)` which overrides/competes with Alembic migrations in production. Should be disabled/modified.

### Code Organization
- Current router endpoints perform raw DB querying instead of delegating to a dedicated services layer. Should transition to Service pattern as complexity grows.
- JWT `SECRET_KEY` and `ALGORITHM` are hardcoded in import schemas or missing configuration handles.
