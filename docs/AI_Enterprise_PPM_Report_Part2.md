# AI-Powered Enterprise PPM — Complete Project Analysis (Part 2/4)

# 7. Authentication & Authorization

## 7.1 Registration Flow
**Endpoint:** `POST /api/auth/register` → [routers/auth.py:18-50](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/routers/auth.py#L18-L50)

1. Pydantic validates: name, email (regex `^\S+@\S+\.\S+$`), password (min 8 chars), role, org_name
2. Check duplicate email: `User.email == request.email AND is_deleted == False`
3. Create `Organization` → `db.flush()` to get `org.id`
4. Create `User` with `hash_password(request.password)` → bcrypt with random salt
5. `db.commit()` — single transaction for both org + user
6. Generate JWT: `create_access_token(data={"sub": user.email})`
7. Return `{"access_token": "...", "token_type": "bearer"}`

## 7.2 Login Flow
**Endpoint:** `POST /api/auth/login` → [routers/auth.py:52-73](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/routers/auth.py#L52-L73)

1. Query user by email (filtered by `is_deleted == False`)
2. **Timing-attack prevention:** If user not found, still calls `verify_password()` against a dummy hash
3. If invalid credentials → HTTP 401 "Incorrect email or password"
4. If user inactive → HTTP 400 "Inactive user account"
5. Generate JWT → return token

## 7.3 Google OAuth Flow
**Endpoint:** `POST /api/auth/google` → [routers/auth.py:79-180](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/routers/auth.py#L79-L180)

1. If `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` configured: exchange auth code with Google OAuth2
2. If not configured: **Developer Mock Mode** — accepts `mock_email` for testing
3. If user exists → generate JWT
4. If new user → auto-create Organization (domain-based naming) + User (ADMIN role, random password)

## 7.4 JWT Token Structure
- **Algorithm:** HS256
- **Secret:** `SECRET_KEY` from environment
- **Payload:** `{"sub": "user@email.com", "exp": <UTC+1hr>}`
- **Validation:** [core/auth.py:25-42](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/core/auth.py#L25-L42) — decode → extract email → query User

## 7.5 Role-Based Access Control
**Function:** `require_role(allowed_roles)` → [core/auth.py:44-52](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/core/auth.py#L44-L52)
- Returns FastAPI dependency that checks `current_user.role.value in allowed_roles`
- Returns HTTP 403 if role mismatch
- **Note:** Defined but not actively used on any endpoint — all endpoints currently use `get_current_user` only

## 7.6 Protected Routes
Every API endpoint (except `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/google`, `GET /`) requires JWT via `Depends(get_current_user)`.

---

# 8. API Documentation

## 8.1 Authentication (`/api/auth`)

| Method | Route | Purpose | Auth | Request Body | Response |
|---|---|---|---|---|---|
| POST | `/register` | Register user + org | No | `{name, email, password, role, organization_name, industry?, employee_count?}` | `{access_token, token_type}` |
| POST | `/login` | Login | No | `{email, password}` | `{access_token, token_type}` |
| GET | `/me` | Get current user profile | Yes | — | `{id, name, email, role, is_active, organization_id}` |
| POST | `/google` | Google OAuth login | No | `{code?, mock_email?, mock_name?}` | `{access_token, token_type}` |

## 8.2 Organization (`/api/org`)

| Method | Route | Purpose | Auth | Request Body | Response |
|---|---|---|---|---|---|
| POST | `/` | Create organization | Yes | `{name, description?, industry?, employee_count?}` | OrganizationResponse |
| GET | `/` | List user's org | Yes | — | OrganizationResponse[] |

## 8.3 Assessment (`/api/assessments`)

| Method | Route | Purpose | Auth | Request Body | Response |
|---|---|---|---|---|---|
| GET | `/frameworks` | List maturity frameworks | Yes | — | `[{id, name, description, version}]` |
| POST | `/start` | Start new assessment | Yes | `{org_id, framework_id}` | AssessmentResponse |
| GET | `/{id}/questions` | Get assessment questions | Yes | — | `[{id, question_text, category_name, max_score}]` |
| POST | `/{id}/submit` | Submit answers + AI scoring | Yes | `{responses: [{question_id, score?, text_response?}]}` | AssessmentResultsResponse |
| GET | `/{id}/results` | Retrieve scored results | Yes | — | AssessmentResultsResponse |

**AssessmentResultsResponse:** `{assessment_id, status, overall_score, overall_level, scores: [{category_id, category_name, score, level, ai_summary}], completed_at}`

## 8.4 Projects (`/api/projects`)

| Method | Route | Purpose | Auth | Request Body | Response |
|---|---|---|---|---|---|
| GET | `/` | List projects (org-scoped) | Yes | Query: `org_id?` | Project[] |
| GET | `/{id}/summary` | Detailed project summary | Yes | — | `{project, risks[], resources[], sprints[]}` |

## 8.5 Assistant (`/api/assistant`)

| Method | Route | Purpose | Auth | Request Body | Response |
|---|---|---|---|---|---|
| POST | `/conversations` | Create conversation | Yes | `{org_id, title?}` | `{id, title}` |
| GET | `/conversations` | List conversations | Yes | Query: `org_id` | Conversation[] |
| GET | `/conversations/{id}/messages` | Get messages | Yes | — | Message[] |
| POST | `/chat` | Send message (non-streaming) | Yes | `{org_id, conversation_id?, message}` | `{conversation_id, agent, agent_key, response}` |
| POST | `/chat/stream` | Send message (SSE streaming) | Yes | `{org_id, conversation_id?, message}` | SSE events: meta→tokens→done |
| GET | `/recommendations` | Get AI recommendations | Yes | Query: `org_id` | Recommendation[] |

---

# 9. AI Features Analysis

## 9.1 AI Integration Architecture

The project implements a **dual-mode AI system**: every AI feature has both an **LLM path** (OpenAI gpt-4o-mini via LangChain) and a **rule-based fallback** when no API key is configured.

```
User Question
     │
     ├── Diagnostic keywords? → Root Cause Analysis Service
     │                              ├── LLM: ChatPromptTemplate → gpt-4o-mini → JSON
     │                              └── Fallback: Rule-based heuristics
     │
     ├── SQL keywords? → NL-to-SQL Service
     │                       ├── LLM: Schema-aware prompt → SQL generation
     │                       └── Fallback: Keyword → predefined SQL mapping
     │
     └── Default → Multi-Agent Orchestrator
                       ├── classify_question() → keyword scoring
                       ├── RiskAgent     (LLM prompt / fallback parser)
                       ├── ResourceAgent (LLM prompt / fallback parser)
                       └── TimelineAgent (LLM prompt / fallback parser)
```

## 9.2 AI Evaluator ([ai_evaluator.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/services/ai_evaluator.py))
- **Purpose:** Score qualitative assessment responses (1-5) with strengths, gaps, recommendations
- **LLM Mode:** `gpt-4o-mini`, temperature=0.2, structured JSON output prompt
- **Fallback:** Keyword matching (`adhoc`→1, `some`→2, `automated`→4, `optimizing`→5, default→3)
- **Output:** `{score, level, gaps[], strengths[], recommendation}`

## 9.3 Root Cause Analysis ([root_cause.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/services/root_cause.py))
- **Purpose:** Diagnose why projects are delayed/at-risk
- **Data gathered:** Budget %, risk severity, sprint velocity trends, team size, completion rates
- **LLM Mode:** System prompt as "Senior PMO Portfolio Director", returns structured JSON
- **Fallback:** 4 rule checks — budget >90%, high-severity risks, sprint completion <70%, team size <4
- **Output:** `{health_summary, primary_issues[], root_causes[], mitigations[], analyzed_by}`

## 9.4 NL-to-SQL Engine ([nl_to_sql.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/services/nl_to_sql.py))
- **Purpose:** Translate natural language → safe PostgreSQL SELECT queries
- **Security:** RESTRICTED_KEYWORDS regex blocks DROP/DELETE/INSERT/UPDATE/etc.; must start with SELECT
- **LLM Mode:** Full schema definition in prompt; org_id scoping enforced
- **Fallback:** 6 keyword categories → predefined SQL templates (budget, risk, delay, resource, sprint, default)
- **Safety:** UUID validation on org_id; secondary fallback if LLM-generated SQL fails

## 9.5 Multi-Agent Orchestrator ([orchestrator.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/agents/orchestrator.py))
- **Classification:** Keyword scoring across 3 agent domains (risk: 8 keywords, resource: 10 keywords, timeline: 10 keywords)
- **Default:** If no keywords match → routes to RiskAgent (broadest coverage)
- **Each agent:** Inherits `BaseAgent` → `_run_llm()` with domain-specific system prompt OR `_run_fallback()` with context parsing

## 9.6 Context Builder ([context_builder.py](file:///d:/Projects/dsa%20project/ai-enterprise-ppm/backend/app/services/context_builder.py))
- Compiles all org projects into a structured text string
- Includes: status, health, budget %, velocity trends, top 5 risks, team allocation, sprint history
- Portfolio summary: counts by status, total budget/spend
- This string is injected into every agent's LLM prompt as context

## 9.7 Prompt Engineering Approach
All prompts follow a consistent pattern:
1. **System role definition** with years of experience and domain expertise
2. **Structured output format** specified (numbered sections or JSON schema)
3. **Explicit constraints** (reference actual data, be specific, be actionable)
4. **Temperature control** (0.0-0.2 for factual analysis)

---

# 10. Module-wise Breakdown

## Module 1: Authentication & Organization Management
- **Objective:** Multi-tenant user management with secure authentication
- **Features:** Registration, login, Google OAuth, role-based users, organization isolation
- **Database:** `users`, `organizations` tables
- **APIs:** 4 auth endpoints + 2 org endpoints
- **Frontend:** Login/Register page, Google callback page, Navbar with user profile
- **Status:** ✅ Complete

## Module 2: Maturity Assessment Engine
- **Objective:** Structured PMO maturity evaluation with AI-powered scoring
- **Features:** Framework browsing, assessment creation, slide-based questionnaire, AI text evaluation, weighted scoring, radar chart visualization, AI action plans
- **Database:** `maturity_frameworks`, `assessment_categories`, `assessment_questions`, `assessments`, `assessment_responses`, `maturity_scores`
- **APIs:** 5 assessment endpoints
- **Frontend:** Framework list page, questions slide-deck, results dashboard with Recharts radar
- **Status:** ✅ Complete

## Module 3: Project Intelligence
- **Objective:** Portfolio tracking with detailed project metrics
- **Features:** Project listing, detailed summaries with risks/resources/sprints, org-scoped access
- **Database:** `projects`, `project_risks`, `project_resources`, `sprint_data`
- **APIs:** 2 project endpoints
- **Frontend:** Data accessed via assistant chat (no dedicated project dashboard page)
- **Status:** ✅ Backend Complete · ⚠️ No dedicated frontend page

## Module 4: AI PMO Assistant
- **Objective:** Conversational AI for project intelligence queries
- **Features:** Multi-agent routing, SSE streaming, conversation history, suggested starters, markdown rendering
- **Database:** `conversations`, `ai_messages`
- **APIs:** 6 assistant endpoints (chat, stream, conversations CRUD, messages, recommendations)
- **Frontend:** Full chat interface with sidebar, streaming display, table rendering
- **Status:** ✅ Complete

## Module 5: Root Cause Analysis
- **Objective:** Automated diagnosis of project health issues
- **Features:** Project name matching, budget/risk/sprint/resource analysis, LLM + fallback
- **Database:** Reads from `projects`, `project_risks`, `project_resources`, `sprint_data`
- **APIs:** Triggered via assistant chat (keyword detection)
- **Frontend:** Results rendered as markdown in chat
- **Status:** ✅ Complete

## Module 6: NL-to-SQL Engine
- **Objective:** Allow natural language database queries
- **Features:** SQL generation, safety validation, result formatting as markdown tables, fallback queries
- **Database:** Executes raw SELECT queries against portfolio tables
- **APIs:** Triggered via assistant chat (keyword detection)
- **Frontend:** Results rendered as styled HTML tables in chat
- **Status:** ✅ Complete

## Module 7: Recommendations Engine
- **Objective:** AI-generated portfolio recommendations
- **Features:** Recommendation storage with type/priority/action_items
- **Database:** `ai_recommendations` table
- **APIs:** `GET /api/assistant/recommendations`
- **Frontend:** API client exists (`fetchRecommendations`)
- **Status:** ⚠️ Partially Complete — table exists, API exists, but no service to generate recommendations automatically
