from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.assessment import (
    AssessmentResponse,
    AssessmentQuestion,
    AssessmentCategory,
    MaturityScore,
    Assessment
)

def get_level(score: float) -> str:
    if score <= 1.0:
        return "Initial"
    elif score <= 2.0:
        return "Developing"
    elif score <= 3.0:
        return "Defined"
    elif score <= 4.0:
        return "Managed"
    else:
        return "Optimizing"

def compute_scores(assessment_id: str, db: Session) -> dict:
    # Fetch all responses for this assessment
    responses = db.query(AssessmentResponse).filter(
        AssessmentResponse.assessment_id == assessment_id
    ).all()

    # Group responses by category
    cat_scores = {}
    for r in responses:
        q = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == r.question_id).first()
        if q and r.score is not None:
            cat_id = str(q.category_id)
            cat_scores.setdefault(cat_id, []).append(r.score)

    # Load all categories for this framework (via assessment)
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise ValueError(f"Assessment {assessment_id} not found")
    
    categories = db.query(AssessmentCategory).filter(
        AssessmentCategory.framework_id == assessment.framework_id
    ).all()

    results = []
    total_score = 0.0
    valid_categories_count = 0

    # Clean existing scores first to prevent duplicate rows on re-submission
    db.query(MaturityScore).filter(MaturityScore.assessment_id == assessment_id).delete()

    for cat in categories:
        scores = cat_scores.get(str(cat.id), [])
        if scores:
            avg = sum(scores) / len(scores)
        else:
            avg = 1.0  # Default fallback score
            
        avg_rounded = round(float(avg), 2)
        level = get_level(avg_rounded)
        
        # Add to total overall calculation
        total_score += avg_rounded
        valid_categories_count += 1

        score_obj = MaturityScore(
            assessment_id=assessment_id,
            category_id=cat.id,
            score=Decimal(str(avg_rounded)),
            level=level,
            ai_summary=None  # Will be populated by AI evaluator later if key exists
        )
        db.add(score_obj)
        results.append(score_obj)

    overall_avg = round(total_score / valid_categories_count, 2) if valid_categories_count > 0 else 1.0
    
    # Update assessment status and completed_at timestamp
    from datetime import datetime
    assessment.status = "completed"
    assessment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "overall_score": overall_avg,
        "overall_level": get_level(overall_avg),
        "scores": results
    }
