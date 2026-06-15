"""
Orchestrator — classifies user questions and routes them to the appropriate specialist agent.
"""
from app.agents.risk_agent import RiskAgent
from app.agents.resource_agent import ResourceAgent
from app.agents.timeline_agent import TimelineAgent

AGENTS = {
    "risk": RiskAgent(),
    "resource": ResourceAgent(),
    "timeline": TimelineAgent(),
}

RISK_KEYWORDS = ["risk", "issue", "blocker", "critical", "threat", "mitigation", "severity", "danger"]
RESOURCE_KEYWORDS = ["resource", "team", "burnout", "allocation", "staffing", "capacity", "hire", "headcount", "skill", "member"]
TIMELINE_KEYWORDS = ["delay", "timeline", "deadline", "sprint", "velocity", "schedule", "late", "overdue", "milestone", "eta"]


def classify_question(question: str) -> str:
    """Route a user question to the appropriate specialist agent."""
    q = question.lower()

    risk_score = sum(1 for w in RISK_KEYWORDS if w in q)
    resource_score = sum(1 for w in RESOURCE_KEYWORDS if w in q)
    timeline_score = sum(1 for w in TIMELINE_KEYWORDS if w in q)

    scores = {"risk": risk_score, "resource": resource_score, "timeline": timeline_score}
    best = max(scores, key=scores.get)

    # If no keywords matched, default to risk (broadest)
    if scores[best] == 0:
        return "risk"
    return best


def route(question: str, context: str) -> dict:
    """Classify question and route to the correct agent."""
    agent_key = classify_question(question)
    agent = AGENTS[agent_key]
    result = agent.run(context, question)
    result["agent_key"] = agent_key
    return result
