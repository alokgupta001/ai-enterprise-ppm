# Codebase Mapping — APIs
> Last mapped: 2026-06-15

## Active HTTP API Endpoints

### Organization Module
- `POST /api/org/` — Register a new organization.
- `GET /api/org/` — Retrieve list of all active organizations.

### Assessment Module
- `POST /api/assessments/start` — Start a new maturity assessment for an organization.
- `POST /api/assessments/{assessment_id}/submit` — (Planned) Submit answers for all questions.
- `GET /api/assessments/{assessment_id}/results` — (Planned) Retrieve categories scores, overall level, and AI details.

### Authentication & User Module (Planned)
- `POST /api/auth/register` — Register a new organization admin.
- `POST /api/auth/login` — Login to retrieve JWT access tokens.
- `GET /api/auth/me` — Retrieve current authenticated user profile.

### Project Module (Planned)
- `POST /api/projects/` — Create new project.
- `GET /api/projects/` — List projects for the current user's organization.
- `GET /api/projects/{project_id}/summary` — Detailed project metric summary, risks, and sprint velocity.

### Conversational PMO Assistant (Planned)
- `POST /api/assistant/chat` — Natural language chat endpoint with the PMO Orchestrator.
- `POST /api/assistant/chat/stream` — Streaming SSE chat endpoint.
- `GET /api/assistant/recommendations` — Fetch structured AI recommendations.
