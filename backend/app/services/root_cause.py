"""
Root Cause Analysis Service.
Diagnoses issues in delayed or at-risk projects, providing detailed explanations
and actionable mitigations. Supports LLM parsing and a rule-based fallback model.
"""
import os
import json
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectRisk, ProjectResource, SprintData

OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))


def run_root_cause_analysis(project_id_or_name: str, db: Session) -> dict:
    """Analyze a project's state, determine root causes of delays/risks, and propose mitigations."""
    # Find project by UUID or Name
    project = None
    try:
        import uuid
        project_uuid = uuid.UUID(project_id_or_name)
        project = db.query(Project).filter(
            Project.id == project_uuid,
            Project.is_deleted.is_(False)
        ).first()
    except (ValueError, AttributeError):
        pass

    if not project:
        escaped_name = (
            project_id_or_name
            .replace("%", r"\%")
            .replace("_", r"\_")
        )

        project = db.query(Project).filter(
            Project.name.ilike(f"%{escaped_name}%"),
            Project.is_deleted.is_(False)
        ).first()

    if not project:
        return {
            "status": "error",
            "message": f"Project '{project_id_or_name}' not found."
        }

    # Fetch associated data
    risks = db.query(ProjectRisk).filter(
        ProjectRisk.project_id == project.id,
        ProjectRisk.is_deleted.is_(False)
    ).all()

    resources = db.query(ProjectResource).filter(
        ProjectResource.project_id == project.id,
        ProjectResource.is_deleted.is_(False)
    ).all()

    sprints = db.query(SprintData).filter(
        SprintData.project_id == project.id,
        SprintData.is_deleted.is_(False)
    ).order_by(SprintData.sprint_number).all()

    # Compile structured project stats
    budget_pct = (float(project.budget_used) / float(project.budget)
                  * 100) if (project.budget and float(project.budget) > 0) else 0
    health_score = float(
        project.health_score) if project.health_score is not None else 0
    budget = float(project.budget) if project.budget is not None else 0
    budget_used = float(
        project.budget_used) if project.budget_used is not None else 0
    avg_velocity = sum(s.velocity for s in sprints) / \
        len(sprints) if sprints else 0
    avg_completion = sum(float(s.completion_rate)
                         for s in sprints) / len(sprints) if sprints else 100.0

    project_data = {
        "name": project.name,
        "status": project.status,
        "health_score": health_score,
        "budget": budget,
        "budget_used": budget_used,
        "budget_used_percent": round(budget_pct, 1),
        "team_size": project.team_size,
        "start_date": str(project.start_date),
        "target_end_date": str(project.target_end_date),
        "avg_velocity": round(avg_velocity, 1),
        "avg_sprint_completion": round(avg_completion, 1),
        "risks": [{"description": r.description, "severity": r.severity} for r in risks],
        "resources": [{"name": r.resource_name, "role": r.role, "allocation": r.allocation_percent} for r in resources],
        "sprints": [{"sprint": s.sprint_number, "velocity": s.velocity, "completion": float(s.completion_rate)} for s in sprints]
    }

    if OPENAI_AVAILABLE:
        return _run_llm_analysis(project_data)
    return _run_fallback_analysis(project_data)


def _run_llm_analysis(data: dict) -> dict:
    """Trigger OpenAI analysis for root cause diagnostics."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_retries=1
        )

        system_prompt = (
            "You are a Senior PMO Portfolio Director and Root Cause Diagnostic Expert.\n"
            "Analyze the project data provided and return a structured JSON diagnostic report.\n"
            "The JSON must have the following exact keys:\n"
            "- 'health_summary': A brief paragraph summarizing the project status.\n"
            "- 'primary_issues': List of string problems currently affecting delivery.\n"
            "- 'root_causes': List of string underlying technical/operational root causes.\n"
            "- 'mitigations': List of actionable recommendations to get the project back on track.\n"
            "Return ONLY a raw JSON string."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Analyze this project:\n{project_json}")
        ])

        chain = prompt | llm
        result = chain.invoke({"project_json": json.dumps(data, indent=2)})

        # Clean response string if wrapped in markdown
        cleaned_content = result.content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]

        parsed = json.loads(cleaned_content.strip())
        parsed["analyzed_by"] = "OpenAI Root Cause Diagnostic Engine"
        return parsed
    except Exception as e:
        print(f"[RootCause] LLM analysis failed: {e}. Falling back...")
        return _run_fallback_analysis(data)


def _run_fallback_analysis(data: dict) -> dict:
    """Generate a highly detailed analysis using rule-based heuristics."""
    health_summary = f"Project '{data['name']}' is currently '{data['status']}' with a health score of {data['health_score']}/100. "

    primary_issues = []
    root_causes = []
    mitigations = []

    # 1. Budget Checks
    if data["budget_used_percent"] > 90 and data["status"] != "completed":
        primary_issues.append("Critical budget depletion")
        root_causes.append(
            f"High cash burn rate: {data['budget_used_percent']}% of the ${data['budget']:,.0f} budget has been consumed while work is outstanding.")
        mitigations.append(
            "Initiate immediate scope reduction or request contingency fund release.")

    # 2. Risk Severity Checks
    high_risks = [r["description"] for r in data["risks"]
                  if r["severity"] and r["severity"].lower() == "high"]
    if high_risks:
        for hr in high_risks:
            primary_issues.append(f"Unmitigated high-risk item: {hr[:60]}...")
            root_causes.append(
                f"Lack of active risk mitigation planning for: {hr}")
        mitigations.append(
            "Schedule a dedicated risk-response session with key technical stakeholders to draft mitigation workflows.")

    # 3. Sprint performance and Velocity trends
    if data["avg_sprint_completion"] < 70:
        primary_issues.append("Low sprint delivery completion rate")
        root_causes.append(
            f"Over-commitment in planning: average sprint completion rate is {data['avg_sprint_completion']}%")
        mitigations.append(
            "Reduce sprint planning capacity by 25-30% to align with actual historical team velocity.")

    if len(data["sprints"]) >= 3:
        velocities = [s["velocity"] for s in data["sprints"]]
        if velocities[-1] < velocities[-3] * 0.8:
            primary_issues.append("Declining velocity trend")
            root_causes.append(
                f"Technical debt accumulation or resource blockage causing velocity to fall to {velocities[-1]} points.")
            mitigations.append(
                "Dedicate 20% of the next sprint backlog to technical debt and environment resolution.")

    # 4. Resource Constraints
    if data["team_size"] < 4 and data["status"] in ["delayed", "at_risk"]:
        primary_issues.append("Sub-optimal team size")
        root_causes.append(
            f"Severe resource bottlenecks: Only {data['team_size']} members allocated for a non-performing project.")
        mitigations.append(
            "Cross-allocate at least one senior engineer from an on-track project (e.g. Customer Portal Redesign) to balance capacity.")

    # General summaries based on status
    if data["status"] == "delayed":
        health_summary += "The project has missed key delivery dates and requires immediate corrective actions."
        if not primary_issues:
            primary_issues.append("General timeline delays")
            root_causes.append(
                "Ineffective timeline estimates and scope creep.")
            mitigations.append(
                "Perform a re-baselining of target delivery milestones.")
    elif data["status"] == "at_risk":
        health_summary += "The project shows negative indicators that could threaten ultimate timeline goals if left unaddressed."
    elif data["status"] == "on_track":
        health_summary += "The project is meeting planned targets and milestones successfully."
        mitigations.append(
            "Continue standard agile sprint delivery processes and monitor risk logs.")
    else:
        health_summary += "The project is finished and archived."

    # Remove duplicates
    primary_issues = list(dict.fromkeys(primary_issues))
    root_causes = list(dict.fromkeys(root_causes))
    mitigations = list(dict.fromkeys(mitigations))

    # Add default mitigations if none
    if not mitigations:
        mitigations.append("Review project status in weekly PMO sync.")

    return {
        "health_summary": health_summary,
        "primary_issues": primary_issues,
        "root_causes": root_causes,
        "mitigations": mitigations,
        "analyzed_by": "Rule-Based Fallback Diagnostic Engine"
    }
