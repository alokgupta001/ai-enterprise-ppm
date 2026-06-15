"""
Project CRUD router — list, detail, and summary endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.project import Project, ProjectRisk, ProjectResource, SprintData

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("/")
def list_projects(
    org_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects, optionally filtered by organization."""
    # Users can only see projects from their own organization
    if org_id and org_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="User does not have access to this organization")
    
    # Default to user's organization
    query_org_id = org_id or current_user.organization_id
    if not query_org_id:
        return []
    
    q = db.query(Project).filter(
        Project.is_deleted.is_(False),
        Project.org_id == query_org_id
    )
    projects = q.all()

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "status": p.status,
            "health_score": float(p.health_score) if p.health_score else 0,
            "budget": float(p.budget) if p.budget else 0,
            "budget_used": float(p.budget_used) if p.budget_used else 0,
            "team_size": p.team_size,
            "start_date": str(p.start_date) if p.start_date else None,
            "target_end_date": str(p.target_end_date) if p.target_end_date else None,
        }
        for p in projects
    ]


@router.get("/{project_id}/summary")
def project_summary(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed project summary including risks, resources, and sprint data."""
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted.is_(False)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify user belongs to the project's organization
    if current_user.organization_id != project.org_id:
        raise HTTPException(status_code=403, detail="User does not have access to this project")

    risks = db.query(ProjectRisk).filter(
        ProjectRisk.project_id == project_id,
        ProjectRisk.is_deleted.is_(False)
    ).all()

    resources = db.query(ProjectResource).filter(
        ProjectResource.project_id == project_id,
        ProjectResource.is_deleted.is_(False)
    ).all()

    sprints = db.query(SprintData).filter(
        SprintData.project_id == project_id,
        SprintData.is_deleted.is_(False)
    ).order_by(SprintData.sprint_number).all()

    return {
        "project": {
            "id": str(project.id),
            "name": project.name,
            "status": project.status,
            "health_score": float(project.health_score) if project.health_score else 0,
            "budget": float(project.budget) if project.budget else 0,
            "budget_used": float(project.budget_used) if project.budget_used else 0,
            "team_size": project.team_size,
            "start_date": str(project.start_date) if project.start_date else None,
            "target_end_date": str(project.target_end_date) if project.target_end_date else None,
        },
        "risks": [
            {"id": str(r.id), "description": r.description, "severity": r.severity}
            for r in risks
        ],
        "resources": [
            {
                "id": str(r.id),
                "name": r.resource_name,
                "role": r.role,
                "allocation_percent": r.allocation_percent,
                "skills": r.skills,
            }
            for r in resources
        ],
        "sprints": [
            {
                "sprint_number": s.sprint_number,
                "velocity": s.velocity,
                "completion_rate": float(s.completion_rate) if s.completion_rate else 0,
            }
            for s in sprints
        ],
    }
