from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.core.auth import get_current_user
from app.models.organization import Organization
from app.models.user import User
from app.models.assessment import Assessment, MaturityFramework, AssessmentQuestion, AssessmentCategory, AssessmentResponse, MaturityScore
from app.schemas.assessment import AssessmentCreate, AssessmentResponse as AssessmentResponseSchema, AssessmentSubmit, AssessmentResultsResponse, MaturityScoreResponse
from app.services.scoring import compute_scores
from app.services.ai_evaluator import evaluate_response

router = APIRouter(
    prefix="/api/assessments",
    tags=["Assessment"]
)

@router.get(
    "/frameworks",
    response_model=list,
    status_code=status.HTTP_200_OK
)
def list_frameworks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    frameworks = db.query(MaturityFramework).filter(MaturityFramework.is_deleted.is_(False)).all()
    return [{"id": str(f.id), "name": f.name, "description": f.description, "version": f.version} for f in frameworks]

@router.post(
    "/start",
    response_model=AssessmentResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def start_assessment(
    request: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user belongs to the organization
    if current_user.organization_id != request.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this organization"
        )
    
    organization = db.query(Organization).filter(
        Organization.id == request.org_id,
        Organization.is_deleted.is_(False)
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    framework = db.query(MaturityFramework).filter(
        MaturityFramework.id == request.framework_id
    ).first()

    if not framework:
        raise HTTPException(
            status_code=404,
            detail="Framework not found"
        )

    assessment = Assessment(
        org_id=request.org_id,
        framework_id=request.framework_id,
        status="in_progress"
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment

@router.get(
    "/{assessment_id}/questions",
    response_model=list,
    status_code=status.HTTP_200_OK
)
def get_assessment_questions(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Verify user belongs to the organization
    if current_user.organization_id != assessment.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this assessment"
        )
        
    questions = db.query(AssessmentQuestion).join(AssessmentCategory).filter(
        AssessmentCategory.framework_id == assessment.framework_id,
        AssessmentQuestion.is_deleted.is_(False)
    ).order_by(AssessmentCategory.order_index, AssessmentQuestion.order_index).all()

    result = []
    for q in questions:
        cat = db.query(AssessmentCategory).filter(AssessmentCategory.id == q.category_id).first()
        result.append({
            "id": str(q.id),
            "question_text": q.question_text,
            "category_name": cat.name if cat else "General",
            "max_score": q.max_score
        })
    return result

@router.post(
    "/{assessment_id}/submit",
    response_model=AssessmentResultsResponse,
    status_code=status.HTTP_200_OK
)
def submit_responses(
    assessment_id: UUID,
    payload: AssessmentSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Verify user belongs to the organization
    if current_user.organization_id != assessment.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this assessment"
        )

    # Clean existing responses to allow re-submission
    db.query(AssessmentResponse).filter(AssessmentResponse.assessment_id == assessment_id).delete()
    db.flush()

    category_summaries = {}

    for r in payload.responses:
        q = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == r.question_id).first()
        if not q:
            continue

        score_value = r.score
        rec_text = None

        # Process free-text responses with the AI Evaluator
        if r.text_response and r.text_response.strip():
            cat = db.query(AssessmentCategory).filter(AssessmentCategory.id == q.category_id).first()
            category_name = cat.name if cat else "General"
            
            ai_eval = evaluate_response(category_name, q.question_text, r.text_response)
            
            if score_value is None:
                score_value = ai_eval.get("score", 3)
            
            rec_text = (
                f"Strength: {', '.join(ai_eval.get('strengths', []))}. "
                f"Gap: {', '.join(ai_eval.get('gaps', []))}. "
                f"Recommendation: {ai_eval.get('recommendation', '')}"
            )
            
            # Group recommendations by category
            category_summaries.setdefault(str(q.category_id), []).append(rec_text)

        # Fallback to slider score if no text response
        if score_value is None:
            score_value = 3

        response_obj = AssessmentResponse(
            assessment_id=assessment_id,
            question_id=r.question_id,
            score=score_value,
            text_response=r.text_response
        )
        db.add(response_obj)

    # Calculate numeric scores (compute_scores will handle its own transaction)
    scores_result = compute_scores(str(assessment_id), db)

    # Attach compiled summaries back to the computed MaturityScore objects
    overall_scores = []
    for s in db.query(MaturityScore).filter(MaturityScore.assessment_id == assessment_id).all():
        cat = db.query(AssessmentCategory).filter(AssessmentCategory.id == s.category_id).first()
        cat_name = cat.name if cat else "Unknown Category"
        
        recs = category_summaries.get(str(s.category_id), [])
        if recs:
            s.ai_summary = " | ".join(recs)
        else:
            s.ai_summary = "No qualitative answers submitted. Standard scores calculated."
        
        db.add(s)
        
        overall_scores.append(MaturityScoreResponse(
            category_id=s.category_id,
            category_name=cat_name,
            score=float(s.score),
            level=s.level,
            ai_summary=s.ai_summary
        ))

    assessment.completed_at = datetime.utcnow()
    db.commit()  # Single commit at the end of the request handler

    return AssessmentResultsResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        overall_score=scores_result["overall_score"],
        overall_level=scores_result["overall_level"],
        scores=overall_scores,
        completed_at=assessment.completed_at
    )

@router.get(
    "/{assessment_id}/results",
    response_model=AssessmentResultsResponse,
    status_code=status.HTTP_200_OK
)
def get_results(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Verify user belongs to the organization
    if current_user.organization_id != assessment.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this assessment"
        )

    scores = db.query(MaturityScore).filter(MaturityScore.assessment_id == assessment_id).all()
    overall_scores = []
    total_score = 0.0
    valid_count = 0

    for s in scores:
        cat = db.query(AssessmentCategory).filter(AssessmentCategory.id == s.category_id).first()
        cat_name = cat.name if cat else "Unknown Category"
        
        total_score += float(s.score)
        valid_count += 1

        overall_scores.append(MaturityScoreResponse(
            category_id=s.category_id,
            category_name=cat_name,
            score=float(s.score),
            level=s.level,
            ai_summary=s.ai_summary
        ))

    overall_avg = round(total_score / valid_count, 2) if valid_count > 0 else 1.0
    from app.services.scoring import get_level

    return AssessmentResultsResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        overall_score=overall_avg,
        overall_level=get_level(overall_avg),
        scores=overall_scores,
        completed_at=assessment.completed_at
    )