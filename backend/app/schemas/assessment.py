from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel

class AssessmentCreate(BaseModel):
    org_id: UUID
    framework_id: UUID

    model_config = {
        "extra": "forbid"
    }

class AssessmentResponse(BaseModel):
    id: UUID
    org_id: UUID
    framework_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class ResponseSubmit(BaseModel):
    question_id: UUID
    score: Optional[int] = None
    text_response: Optional[str] = None

    model_config = {
        "extra": "forbid"
    }

class AssessmentSubmit(BaseModel):
    responses: List[ResponseSubmit]

    model_config = {
        "extra": "forbid"
    }

class MaturityScoreResponse(BaseModel):
    category_id: UUID
    category_name: str
    score: float
    level: str
    ai_summary: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class AssessmentResultsResponse(BaseModel):
    assessment_id: UUID
    status: str
    overall_score: float
    overall_level: str
    scores: List[MaturityScoreResponse]
    completed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }