# AI-Powered Enterprise PPM — Complete Project Analysis (Part 1/4)

> **Prepared for:** College Project Viva · Internship Review · Technical Presentation · Resume
> **Date:** June 19, 2026 · **Analyst:** Senior Software Architect / Technical Lead

---

# 1. Executive Summary

## What This Project Is
**AI-Powered Enterprise PPM (Project Portfolio Management)** is a full-stack web application that enables organizations to assess their project management maturity, manage project portfolios, and receive AI-powered diagnostic insights. It combines a structured maturity assessment engine with an intelligent conversational assistant backed by multi-agent AI architecture.

## Business Problem Solved
Most enterprises lack a systematic, data-driven way to evaluate their project management capabilities. Traditional PMO assessments are manual, subjective, and produce static reports. This platform:
- **Automates maturity evaluation** with AI-scored qualitative responses
- **Provides real-time root cause diagnosis** of delayed/at-risk projects
- **Enables natural language database queries** (NL-to-SQL) so non-technical users can extract project insights
- **Routes questions to specialist AI agents** (Risk, Resource, Timeline)

## Target Users
| Role | Usage |
|---|---|
| PMO Directors | Portfolio-level health monitoring, maturity benchmarking |
| Project Managers | Risk identification, sprint analysis, resource insights |
| Executives | High-level dashboards, investment decision support |
| IT Administrators | System setup, user/org management |

## Key Features (Verified from Code)
1. **JWT Authentication** with bcrypt hashing and Google OAuth integration
2. **Organization-scoped multi-tenancy** with role-based access (ADMIN, PMO, MANAGER, EXECUTIVE)
3. **Maturity Assessment Engine** — 5 categories, 25 questions, AI-evaluated text responses
4. **AI Evaluator** — LangChain + OpenAI (gpt-4o-mini) with rule-based fallback
5. **Root Cause Analysis** — Automated diagnosis of project health issues
6. **NL-to-SQL Engine** — Natural language → PostgreSQL SELECT queries
7. **Multi-Agent Orchestrator** — Risk, Resource, and Timeline specialist agents
8. **SSE Streaming Chat** — Real-time token-by-token AI response streaming
9. **Radar Chart Visualization** — Recharts-powered maturity distribution
10. **Seed Data System** — 5 realistic projects with risks, resources, sprint data

## Expected Outcomes
- Quantified maturity scores (1-5 scale across 5 PMO dimensions)
- AI-generated action plans per assessment category
- Conversational project intelligence accessible via natural language
- Exportable assessment reports (print-ready)

---

# 2. Project Overview

| Attribute | Detail |
|---|---|
| **Project Name** | AI-Powered Enterprise PPM Platform |
| **Repository** | `github.com/alokgupta001/ai-enterprise-ppm` |
| **Project Goal** | Build an AI-integrated platform for enterprise project portfolio management maturity assessment and intelligence |
| **Problem Statement** | Organizations lack automated, AI-driven tools to assess PMO maturity, diagnose project health issues, and derive actionable portfolio insights |
| **Existing Limitations** | Manual Excel-based assessments, no AI scoring, no root cause analysis, fragmented project data across tools |
| **Proposed Solution** | Full-stack platform with automated maturity scoring, AI evaluation of qualitative responses, multi-agent conversational assistant, and natural language database querying |
| **Scope** | Module 1: Enterprise Assessment Engine · Module 2: AI PMO Intelligence Assistant |

---

# 3. Complete Technology Stack Analysis

## 3.1 Backend Technologies

### Python 3.x
- **What:** General-purpose programming language
- **Why chosen:** Rich ecosystem for AI/ML (LangChain, OpenAI), strong web framework support (FastAPI), excellent ORM libraries
- **Alternatives:** Node.js, Java Spring Boot, Go
- **Advantage:** Fastest path to AI integration; LangChain is Python-first
- **Usage in project:** All backend logic — routers, models, services, agents

### FastAPI v0.115.6
- **What:** Modern async Python web framework with automatic OpenAPI docs
- **Why chosen:** Native async support, auto-generated Swagger UI, Pydantic validation, dependency injection
- **Alternatives:** Django REST Framework, Flask, Express.js
- **Advantage:** 3-10x faster than Flask; built-in request validation; SSE streaming support
- **Usage:** Entry point ([main.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/main.py)), 5 routers, CORS middleware, health check

### SQLAlchemy v2.0.51
- **What:** Python SQL toolkit and ORM
- **Why chosen:** Mature, feature-rich ORM with relationship management, migration support
- **Alternatives:** Tortoise ORM, Peewee, Django ORM
- **Advantage:** Full control over SQL generation; supports complex joins; PostgreSQL-native UUID columns
- **Usage:** All 11 ORM models across 4 files; `BaseMixin` for shared columns (id, timestamps, soft-delete)

### Alembic v1.18.4
- **What:** Database migration tool for SQLAlchemy
- **Why chosen:** Industry standard for SQLAlchemy migrations; supports upgrade/downgrade
- **Alternatives:** Manual SQL scripts, Django migrations
- **Advantage:** Version-controlled schema changes; data seeding via migrations
- **Usage:** 5 migration versions including schema creation and assessment framework seeding

### PostgreSQL
- **What:** Advanced open-source relational database
- **Why chosen:** Native UUID support, JSONB columns, robust full-text search, enterprise-grade
- **Alternatives:** MySQL, SQLite, MongoDB
- **Advantage:** UUID primary keys, JSONB for flexible data (action_items), Numeric precision for scores
- **Usage:** Primary data store; connected via `psycopg2-binary`; 11 tables

### JWT Authentication (python-jose v3.5.0)
- **What:** JSON Web Token implementation for stateless auth
- **Why chosen:** Stateless, scalable, standard bearer token pattern
- **Alternatives:** Session-based auth, OAuth2 only, API keys
- **Advantage:** No server-side session storage; works with SPA frontends
- **Usage:** Token creation in [auth.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/core/auth.py); HS256 algorithm; 1-hour expiry

### LangChain (langchain-openai)
- **What:** Framework for building LLM-powered applications
- **Why chosen:** Structured prompt templates, chain composition, multiple LLM provider support
- **Alternatives:** Direct OpenAI SDK, Haystack, LlamaIndex
- **Advantage:** Abstracted prompt engineering; easy provider switching; retry logic
- **Usage:** AI evaluator, root cause analysis, NL-to-SQL translation, all 3 specialist agents

### bcrypt v5.0.0
- **What:** Password hashing library using Blowfish cipher
- **Why chosen:** Industry-standard adaptive hashing; resistant to brute-force
- **Alternatives:** Argon2, scrypt, PBKDF2
- **Advantage:** Built-in salt generation; configurable work factor
- **Usage:** [security.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/core/security.py) — `hash_password()` and `verify_password()`

### Other Backend Libraries
| Library | Purpose |
|---|---|
| `uvicorn v0.34.0` | ASGI server for FastAPI |
| `pydantic v2.10.4` | Request/response validation |
| `python-dotenv v1.2.2` | Environment variable loading |
| `nltk v3.9.4` | Natural language processing (available but not actively used) |
| `textblob v0.18.0` | Text sentiment analysis (available but not actively used) |
| `python-docx v1.2.0` | Document generation capability |
| `requests` | Google OAuth HTTP calls |

## 3.2 Frontend Technologies

### Next.js v16.2.7
- **What:** React meta-framework with SSR, routing, and optimization
- **Why chosen:** File-based routing, server components, optimized builds
- **Alternatives:** Vite + React Router, Remix, Angular
- **Advantage:** App Router with nested layouts; automatic code splitting
- **Usage:** All pages under `/app` directory; layout with sidebar navigation

### React v19.2.4
- **What:** UI component library
- **Usage:** All interactive components — forms, chat interface, assessment flow

### TypeScript v5
- **What:** Typed superset of JavaScript
- **Usage:** All `.tsx` files with interface definitions for Conversation, Message types

### Tailwind CSS v4
- **What:** Utility-first CSS framework
- **Usage:** Every component; dark theme with zinc color palette; custom oklch color variables

### Additional Frontend Libraries
| Library | Purpose |
|---|---|
| `axios v1.16.1` | HTTP client with interceptors for JWT |
| `recharts v3.8.1` | Radar chart visualization on results page |
| `framer-motion v12.40.0` | Animation library (imported, available) |
| `lucide-react v1.17.0` | Icon library (30+ icons used) |
| `shadcn v4.10.0` | UI component system (button component) |
| `radix-ui v1.4.3` | Headless UI primitives |

## 3.3 Infrastructure

| Component | Technology |
|---|---|
| Version Control | Git + GitHub |
| Environment Management | `.env` files (backend + frontend) |
| API Architecture | RESTful with SSE streaming |
| Database Migrations | Alembic |
| Package Management | pip (backend) + npm (frontend) |

---

# 4. Folder Structure Analysis

```
ai-enterprise-ppm/
├── .gitignore                    # Excludes venv, node_modules, .env, __pycache__
├── backend/
│   ├── .env                      # Database URL, JWT secret, CORS origins
│   ├── requirements.txt          # 37 Python dependencies
│   ├── alembic.ini               # Alembic migration configuration
│   ├── alembic/
│   │   ├── env.py                # Migration environment setup
│   │   └── versions/             # 5 migration scripts (schema + seed data)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app entry point, CORS, router registration
│   │   ├── database.py           # SQLAlchemy engine, SessionLocal, get_db()
│   │   ├── seed.py               # Project portfolio seed data (5 projects)
│   │   ├── core/
│   │   │   ├── config.py         # All env var loading (JWT, DB, AI, OAuth, CORS)
│   │   │   ├── auth.py           # JWT create/validate, get_current_user, require_role
│   │   │   └── security.py       # bcrypt hash_password, verify_password
│   │   ├── models/
│   │   │   ├── __init__.py       # Model registration for table creation
│   │   │   ├── base.py           # BaseMixin (UUID id, timestamps, soft-delete)
│   │   │   ├── enums.py          # UserRole enum (ADMIN, PMO, MANAGER, EXECUTIVE)
│   │   │   ├── user.py           # User model with org relationship
│   │   │   ├── organization.py   # Organization model
│   │   │   ├── assessment.py     # 6 models: Framework, Category, Question, Assessment, Response, Score
│   │   │   └── project.py        # 6 models: Project, Risk, Resource, Sprint, Conversation, Message, Recommendation
│   │   ├── schemas/
│   │   │   ├── __init__.py       # Schema exports
│   │   │   ├── auth.py           # Register, Login, Token, User, GoogleLogin schemas
│   │   │   ├── organization.py   # OrgCreate, OrgResponse schemas
│   │   │   └── assessment.py     # Assessment CRUD + results schemas
│   │   ├── routers/
│   │   │   ├── auth.py           # /api/auth — register, login, me, google
│   │   │   ├── organization.py   # /api/org — create, list
│   │   │   ├── assessment.py     # /api/assessments — frameworks, start, questions, submit, results
│   │   │   ├── project.py        # /api/projects — list, summary
│   │   │   └── assistant.py      # /api/assistant — chat, stream, conversations, messages, recommendations
│   │   ├── services/
│   │   │   ├── scoring.py        # Maturity score computation + level mapping
│   │   │   ├── ai_evaluator.py   # LLM + rule-based response evaluation
│   │   │   ├── context_builder.py# Portfolio context string generator for LLM prompts
│   │   │   ├── root_cause.py     # Project health diagnosis (LLM + fallback)
│   │   │   ├── nl_to_sql.py      # Natural language → SQL translation
│   │   │   └── assessment_service.py # (empty — planned)
│   │   └── agents/
│   │       ├── __init__.py       # BaseAgent abstract class (LLM + fallback pattern)
│   │       ├── base_agent.py     # Re-export of BaseAgent
│   │       ├── orchestrator.py   # Question classifier + agent router
│   │       ├── risk_agent.py     # Risk analysis specialist
│   │       ├── resource_agent.py # Resource/team analysis specialist
│   │       └── timeline_agent.py # Sprint/timeline analysis specialist
│   └── venv/                     # Python virtual environment
├── frontend/
│   ├── .env.local                # API base URL
│   ├── package.json              # 14 dependencies + 7 dev dependencies
│   ├── components.json           # shadcn/ui configuration
│   ├── next.config.ts            # Next.js configuration
│   ├── tsconfig.json             # TypeScript configuration
│   ├── app/
│   │   ├── layout.tsx            # Root layout — Inter font, dark theme, Navbar
│   │   ├── page.tsx              # Home page (Next.js default — not customized)
│   │   ├── globals.css           # Tailwind + shadcn theme variables (light + dark)
│   │   ├── login/
│   │   │   ├── page.tsx          # Login/Register form + Google OAuth
│   │   │   └── callback/page.tsx # Google OAuth callback handler
│   │   ├── assessments/
│   │   │   ├── page.tsx          # Framework browser + assessment creation
│   │   │   └── [id]/
│   │   │       ├── questions/page.tsx # Slide-based questionnaire with slider + text
│   │   │       └── results/page.tsx   # Radar chart + AI action plan display
│   │   └── assistant/
│   │       └── page.tsx          # Full chat interface with streaming + suggestions
│   ├── components/
│   │   ├── Navbar.tsx            # Sidebar navigation with user profile
│   │   └── ui/button.tsx         # shadcn button component
│   ├── lib/
│   │   ├── api.ts                # Axios client + all API functions (15 exports)
│   │   └── utils.ts              # cn() utility for class merging
│   └── public/                   # Static assets
├── database/
│   └── schema/
│       └── 01_assessment.sql     # (empty — schema managed by Alembic)
└── docs/
    ├── AI-Powered Enterprise PPM.docx
    ├── AI_Enterprise_PPM_Build_Guide.pdf
    ├── AI_PPM_Complete_Guide.pdf
    └── assessment_engine_progress_report.md
```

---

# 5. System Architecture

## Layered Architecture

```
┌─────────────────────────────────────────────┐
│              USER (Browser)                  │
├─────────────────────────────────────────────┤
│         FRONTEND (Next.js 16)                │
│  Login → Assessments → Assistant → Results   │
│  Axios + JWT Token (localStorage)            │
├─────────────────────────────────────────────┤
│           API LAYER (FastAPI)                │
│  /api/auth  /api/org  /api/assessments       │
│  /api/projects  /api/assistant               │
│  CORS · JWT Validation · Pydantic Schemas    │
├─────────────────────────────────────────────┤
│        BUSINESS LOGIC LAYER                  │
│  Scoring Service · AI Evaluator              │
│  Root Cause Analysis · NL-to-SQL             │
│  Context Builder · Agent Orchestrator        │
├─────────────────────────────────────────────┤
│         DATABASE LAYER (PostgreSQL)          │
│  SQLAlchemy ORM · Alembic Migrations         │
│  11 Tables · UUID PKs · Soft Deletes         │
├─────────────────────────────────────────────┤
│            AI LAYER (LangChain)              │
│  OpenAI gpt-4o-mini · Rule-Based Fallbacks   │
│  Risk Agent · Resource Agent · Timeline Agent│
└─────────────────────────────────────────────┘
```

## Request Flow (Assessment Submission Example)
1. User fills questionnaire on `/assessments/[id]/questions`
2. Frontend calls `POST /api/assessments/{id}/submit` with JWT header
3. FastAPI validates JWT → extracts user → verifies org ownership
4. For each text response: `ai_evaluator.evaluate_response()` calls OpenAI (or falls back to rule-based)
5. `scoring.compute_scores()` calculates weighted category averages
6. MaturityScore records created with AI summaries
7. Assessment status set to "completed"
8. JSON response returned → frontend renders radar chart + action plan

## Authentication Flow
1. User submits credentials → `POST /api/auth/login`
2. Backend verifies bcrypt hash (timing-safe: dummy hash used if user not found)
3. JWT created with `sub: email`, `exp: UTC+1hr`, signed with HS256
4. Token stored in `localStorage` on frontend
5. Every API call: Axios interceptor attaches `Authorization: Bearer <token>`
6. `get_current_user()` dependency decodes JWT → queries User → returns or 401

---

# 6. Database Analysis

## 6.1 Entity-Relationship Overview

The database contains **11 tables** organized into 4 domains:

### Domain 1: Identity & Organization
| Table | Purpose | Key Columns |
|---|---|---|
| `organizations` | Multi-tenant org container | id(UUID PK), name, industry, employee_count |
| `users` | User accounts | id(UUID PK), email(unique,indexed), password_hash, role(enum), organization_id(FK) |

**Relationship:** Organization 1→N Users (cascade delete)

### Domain 2: Maturity Assessment
| Table | Purpose | Key Columns |
|---|---|---|
| `maturity_frameworks` | Assessment template | id(UUID PK), name, description, version |
| `assessment_categories` | Question groupings | id(UUID PK), framework_id(FK), name, weight(Numeric), order_index |
| `assessment_questions` | Individual questions | id(UUID PK), category_id(FK), question_text, max_score(5), order_index |
| `assessments` | Assessment run instance | id(UUID PK), org_id(FK), framework_id(FK), status |
| `assessment_responses` | User answers | id(UUID PK), assessment_id(FK), question_id(FK), score(int), text_response |
| `maturity_scores` | Computed category scores | id(UUID PK), assessment_id(FK), category_id(FK), score(Numeric), level, ai_summary |

**Relationships:** Framework 1→N Categories 1→N Questions; Assessment 1→N Responses; Assessment 1→N Scores

### Domain 3: Project Portfolio
| Table | Purpose | Key Columns |
|---|---|---|
| `projects` | Project entities | id(UUID PK), org_id(FK), name, status, health_score, budget, budget_used, team_size, dates |
| `project_risks` | Risk register | id(UUID PK), project_id(FK), description, severity(high/medium/low) |
| `project_resources` | Team members | id(UUID PK), project_id(FK), resource_name, allocation_percent, role, skills |
| `sprint_data` | Agile sprint metrics | id(UUID PK), project_id(FK), sprint_number, velocity, completion_rate |

### Domain 4: AI Assistant
| Table | Purpose | Key Columns |
|---|---|---|
| `conversations` | Chat threads | id(UUID PK), org_id(FK), title |
| `ai_messages` | Chat messages | id(UUID PK), conversation_id(FK), role(user/assistant), content, agent_used |
| `ai_recommendations` | AI-generated recommendations | id(UUID PK), org_id(FK), project_id(FK nullable), type, priority, title, description, action_items(JSON) |

## 6.2 Common Column Pattern (BaseMixin)
Every table inherits from `BaseMixin`:
- `id` — UUID primary key (auto-generated via `uuid4()`)
- `created_at` — UTC timestamp, set on insert
- `updated_at` — UTC timestamp, auto-updated
- `is_deleted` — Boolean soft-delete flag (default: False)

## 6.3 Seeded Assessment Framework
The migration `1cb012775886` seeds:
- **1 Framework:** "Enterprise Project Management Maturity Model v1.0"
- **5 Categories:** Portfolio Governance (1.2w), Agile Delivery (1.1w), Resource Management (1.0w), Risk & Issue Management (1.3w), PMO Capability (1.4w)
- **25 Questions:** 5 per category (text-type, max score 5)

## 6.4 Seeded Project Portfolio (seed.py)
5 realistic projects with complete data:

| Project | Status | Health | Budget | Team | Sprints |
|---|---|---|---|---|---|
| ERP Modernization | at_risk | 62 | $500K | 12 | 5 |
| Mobile App Launch | on_track | 88 | $150K | 6 | 5 |
| Data Migration Platform | delayed | 41 | $200K | 4 | 5 |
| Cloud Infrastructure Migration | on_track | 79 | $350K | 8 | 4 |
| Customer Portal Redesign | completed | 95 | $120K | 5 | 6 |
