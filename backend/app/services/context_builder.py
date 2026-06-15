"""
Context builder — compiles project portfolio data into a structured text string
that can be injected into LLM prompts as context.
"""
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectRisk, ProjectResource, SprintData


def build_project_context(org_id: str, db: Session) -> str:
    """Build a comprehensive project portfolio context string for the AI assistant."""
    projects = db.query(Project).filter(
        Project.org_id == org_id,
        Project.is_deleted.is_(False)
    ).all()

    if not projects:
        return "No projects found for this organization."

    context_parts = []

    for p in projects:
        risks = db.query(ProjectRisk).filter(
            ProjectRisk.project_id == p.id,
            ProjectRisk.is_deleted.is_(False)
        ).all()

        resources = db.query(ProjectResource).filter(
            ProjectResource.project_id == p.id,
            ProjectResource.is_deleted.is_(False)
        ).all()

        sprints = db.query(SprintData).filter(
            SprintData.project_id == p.id,
            SprintData.is_deleted.is_(False)
        ).order_by(SprintData.sprint_number).all()

        # Budget analysis
        budget_pct = round((float(p.budget_used) / float(p.budget)) * 100, 1) if p.budget and float(p.budget) > 0 else 0

        # Sprint velocity trend
        velocity_trend = "stable"
        if len(sprints) >= 3:
            recent = [s.velocity for s in sprints[-3:]]
            if recent[-1] < recent[0] * 0.8:
                velocity_trend = "declining"
            elif recent[-1] > recent[0] * 1.2:
                velocity_trend = "improving"

        risk_summary = "; ".join(
            [f"[{r.severity.upper()}] {r.description}" for r in risks[:5]]
        ) if risks else "No identified risks"

        resource_summary = ", ".join(
            [f"{r.resource_name} ({r.role}, {r.allocation_percent}%)" for r in resources]
        ) if resources else "No resources assigned"

        sprint_summary = ", ".join(
            [f"Sprint {s.sprint_number}: vel={s.velocity}, completion={s.completion_rate}%" for s in sprints]
        ) if sprints else "No sprint data"

        context_parts.append(
            f"PROJECT: {p.name}\n"
            f"  Status: {p.status} | Health Score: {p.health_score}/100\n"
            f"  Budget: ${float(p.budget):,.0f} used ${float(p.budget_used):,.0f} ({budget_pct}%)\n"
            f"  Team Size: {p.team_size} | Start: {p.start_date} | Target End: {p.target_end_date}\n"
            f"  Velocity Trend: {velocity_trend}\n"
            f"  Risks: {risk_summary}\n"
            f"  Team: {resource_summary}\n"
            f"  Sprints: {sprint_summary}\n"
        )

    portfolio_summary = (
        f"PORTFOLIO OVERVIEW: {len(projects)} projects\n"
        f"  On Track: {sum(1 for p in projects if p.status == 'on_track')}\n"
        f"  At Risk: {sum(1 for p in projects if p.status == 'at_risk')}\n"
        f"  Delayed: {sum(1 for p in projects if p.status == 'delayed')}\n"
        f"  Completed: {sum(1 for p in projects if p.status == 'completed')}\n"
        f"  Total Budget: ${sum(float(p.budget) for p in projects):,.0f}\n"
        f"  Total Spent: ${sum(float(p.budget_used) for p in projects):,.0f}\n"
    )

    return portfolio_summary + "\n" + "\n".join(context_parts)
