from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationResponse

router = APIRouter(prefix="/api/org", tags=["Organization"])


# CREATE ORGANIZATION
@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_organization(
    request: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization. User creating it becomes the owner."""
    org = Organization(**request.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Assign the creating user to the organization
    current_user.organization_id = org.id
    db.commit()
    
    return org


# GET ALL ORGANIZATIONS
@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organizations. Users can only see their own organization."""
    if not current_user.organization_id:
        return []
    
    return db.query(Organization).filter(
        Organization.id == current_user.organization_id,
        Organization.is_deleted.is_(False)
    ).all()