"""
NL to SQL Service.
Translates user natural language questions into safe database SELECT queries,
executes them, and returns raw query results. Implements robust fallback queries
for rules-based search when LLM is unavailable.
"""
import os
import re
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine

OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))

# Safety pattern to block malicious database writes or reads
RESTRICTED_KEYWORDS = re.compile(
    r"\b(drop|delete|insert|update|create|alter|truncate|grant|revoke|union|into|load_file|outfile)\b",
    re.IGNORECASE
)


def execute_nl_query(question: str, org_id: str, db: Session) -> dict:
    """Translate natural language to SQL, execute securely, and return results."""
    # Validate org_id is a valid UUID format
    try:
        uuid.UUID(org_id)
    except (ValueError, AttributeError):
        return {
            "query": "",
            "error": "Invalid organization identifier format.",
            "results": []
        }
    
    sql_query = None
    
    if OPENAI_AVAILABLE:
        sql_query = _translate_llm(question, org_id)
        
    if not sql_query:
        sql_query = _translate_fallback(question, org_id)

    # Clean the SQL query (strip markdown, leading/trailing whitespace)
    sql_query = sql_query.strip()
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.startswith("```"):
        sql_query = sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
    sql_query = sql_query.strip()

    # Safety Check: Must start with SELECT and must not contain restricted keywords
    if not sql_query.upper().startswith("SELECT"):
        return {
            "query": sql_query,
            "error": "Query security validation failed: Only SELECT queries are permitted.",
            "results": []
        }
    
    if RESTRICTED_KEYWORDS.search(sql_query):
        return {
            "query": sql_query,
            "error": "Query security validation failed: Restricted database operation keywords detected.",
            "results": []
        }

    try:
        # Run raw SQL select
        result = db.execute(text(sql_query), {"org_id": org_id})
        keys = list(result.keys())
        rows = [dict(zip(keys, row)) for row in result.fetchall()]
        
        # Serialize UUIDs and decimals to standard python strings/floats
        for r in rows:
            for k, v in r.items():
                if hasattr(v, "hex"):  # UUID
                    r[k] = str(v)
                elif hasattr(v, "as_tuple"):  # Decimal/Numeric
                    r[k] = float(v)
                elif hasattr(v, "strftime"):  # Date
                    r[k] = str(v)

        return {
            "query": sql_query,
            "results": rows,
            "error": None
        }
    except Exception as e:
        print(f"[NL_to_SQL] Database execution failed: {e}. SQL was: {sql_query}")
        # Secondary fallback: run basic fallback
        try:
            fb_query = _translate_fallback(question, org_id)
            result = db.execute(text(fb_query), {"org_id": org_id})
            keys = list(result.keys())
            rows = [dict(zip(keys, row)) for row in result.fetchall()]
            for r in rows:
                for k, v in r.items():
                    if hasattr(v, "hex"):
                        r[k] = str(v)
                    elif hasattr(v, "as_tuple"):
                        r[k] = float(v)
                    elif hasattr(v, "strftime"):
                        r[k] = str(v)
            return {
                "query": fb_query,
                "results": rows,
                "error": f"LLM generated query failed; executed fallback. (Error: {str(e)[:80]})"
            }
        except Exception as fb_err:
            return {
                "query": sql_query,
                "error": f"Database execution failed: {str(e)}",
                "results": []
            }


def _translate_llm(question: str, org_id: str) -> str:
    """Use LangChain / OpenAI to generate SQL from user's question."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_retries=1
        )

        system_prompt = (
            "You are a PostgreSQL expert database translator.\n"
            "Translate the user's natural language question into a PostgreSQL SELECT query.\n\n"
            "SCHEMA DEFINITIONS:\n"
            "- projects (id UUID, org_id UUID, name VARCHAR, status VARCHAR, health_score NUMERIC, budget NUMERIC, budget_used NUMERIC, start_date DATE, target_end_date DATE, team_size INTEGER, is_deleted BOOLEAN)\n"
            "- project_risks (id UUID, project_id UUID, description TEXT, severity VARCHAR, is_deleted BOOLEAN)\n"
            "- project_resources (id UUID, project_id UUID, resource_name VARCHAR, allocation_percent INTEGER, role VARCHAR, skills VARCHAR, is_deleted BOOLEAN)\n"
            "- sprint_data (id UUID, project_id UUID, sprint_number INTEGER, velocity INTEGER, completion_rate NUMERIC, is_deleted BOOLEAN)\n\n"
            "RULES:\n"
            f"1. You MUST restrict the query to org_id = '{org_id}' for safety.\n"
            "2. Always add conditions to filter out 'is_deleted = false' on tables where it exists.\n"
            "3. Generate ONLY standard SELECT statements. No updates, drops, etc.\n"
            "4. Return ONLY the raw SQL query, with no markdown tags or introductory text."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Translate: {question}")
        ])

        chain = prompt | llm
        result = chain.invoke({"question": question})
        return result.content.strip()
    except Exception as e:
        print(f"[NL_to_SQL] LLM translation failed: {e}")
        return None


def _translate_fallback(question: str, org_id: str) -> str:
    """Fallback rules to build a safe SELECT query by mapping keywords in the question."""
    q = question.lower()
    
    # 1. Budget overrun or heavy spend
    if "budget" in q or "cost" in q or "spend" in q or "expensive" in q:
        return (
            "SELECT name, status, health_score, budget, budget_used, "
            "round((budget_used/budget)*100, 1) as budget_used_percent "
            "FROM projects "
            f"WHERE org_id = '{org_id}' AND budget > 0 AND is_deleted = false "
            "ORDER BY budget_used_percent DESC"
        )
    
    # 2. At risk or delayed status
    if "at risk" in q or "risk" in q or "danger" in q:
        if "project" in q:
            return (
                "SELECT name, status, health_score, budget, budget_used "
                "FROM projects "
                f"WHERE org_id = '{org_id}' AND (status = 'at_risk' OR health_score < 70) AND is_deleted = false "
                "ORDER BY health_score ASC"
            )
        else:
            return (
                "SELECT p.name as project_name, r.description, r.severity "
                "FROM projects p "
                "JOIN project_risks r ON p.id = r.project_id "
                f"WHERE p.org_id = '{org_id}' AND p.is_deleted = false AND r.is_deleted = false "
                "ORDER BY CASE r.severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END"
            )

    # 3. Delayed status specifically
    if "delay" in q or "late" in q or "behind" in q:
        return (
            "SELECT name, status, health_score, target_end_date "
            "FROM projects "
            f"WHERE org_id = '{org_id}' AND (status = 'delayed' OR target_end_date < CURRENT_DATE) AND is_deleted = false "
            "ORDER BY health_score ASC"
        )

    # 4. Resources and staffing
    if "resource" in q or "staff" in q or "team" in q or "allocation" in q or "assigned" in q:
        return (
            "SELECT p.name as project_name, r.resource_name, r.role, r.allocation_percent, r.skills "
            "FROM projects p "
            "JOIN project_resources r ON p.id = r.project_id "
            f"WHERE p.org_id = '{org_id}' AND p.is_deleted = false AND r.is_deleted = false "
            "ORDER BY r.allocation_percent DESC"
        )

    # 5. Sprint velocity or timeline deliverables
    if "sprint" in q or "velocity" in q or "productivity" in q:
        return (
            "SELECT p.name as project_name, s.sprint_number, s.velocity, s.completion_rate "
            "FROM projects p "
            "JOIN sprint_data s ON p.id = s.project_id "
            f"WHERE p.org_id = '{org_id}' AND p.is_deleted = false AND s.is_deleted = false "
            "ORDER BY p.name, s.sprint_number"
        )

    # Default: List all active projects
    return (
        "SELECT name, status, health_score, budget, team_size "
        "FROM projects "
        f"WHERE org_id = '{org_id}' AND is_deleted = false "
        "ORDER BY name"
    )
