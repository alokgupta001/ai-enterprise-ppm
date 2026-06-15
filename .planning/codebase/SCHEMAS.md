# Codebase Mapping — Schemas
> Last mapped: 2026-06-15

## Pydantic Schemas

### Organization Schemas
- `OrganizationBase` (app/schemas/organization.py): Base fields for organization.
- `OrganizationCreate`: Schema for creation payload.
- `OrganizationResponse`: Outbound serialization schema.

### Authentication & User Schemas
- `RegisterRequest` (app/schemas/auth.py): Payload for admin signup and organization creation.
- `LoginRequest`: Fields validation for token request.
- `TokenResponse`: Returns JWT token and bearer type.

### Assessment Schemas
- `AssessmentCreate` (app/schemas/assessment.py): Request schema containing `org_id` and `framework_id`.
- `AssessmentResponse`: Base output schema.
- `ResponseSubmit`: (Planned) Individual question answer container (question_id, score, text).
- `AssessmentSubmit`: (Planned) Wrapper containing a list of `ResponseSubmit`.
- `MaturityScoreResponse`: (Planned) Outbound score result format.
