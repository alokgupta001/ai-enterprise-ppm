from sqlalchemy import Column, String, Text, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseMixin


# =========================
# Maturity Framework
# =========================
class MaturityFramework(Base, BaseMixin):
    __tablename__ = "maturity_frameworks"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), default="1.0")

    categories = relationship(
        "AssessmentCategory",
        back_populates="framework",
        cascade="all, delete-orphan"
    )


# =========================
# Category
# =========================
class AssessmentCategory(Base, BaseMixin):
    __tablename__ = "assessment_categories"

    framework_id = Column(
        ForeignKey("maturity_frameworks.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(255), nullable=False)
    weight = Column(Numeric(5, 2), default=1.0)
    order_index = Column(Integer, default=0)

    framework = relationship("MaturityFramework", back_populates="categories")

    questions = relationship(
        "AssessmentQuestion",
        back_populates="category",
        cascade="all, delete-orphan"
    )


# =========================
# Question
# =========================
class AssessmentQuestion(Base, BaseMixin):

    __tablename__ = "assessment_questions"

    category_id = Column(
        ForeignKey("assessment_categories.id", ondelete="CASCADE"),
        nullable=False
    )

    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="text")
    max_score = Column(Integer, default=5)
    order_index = Column(Integer, default=0)

    category = relationship("AssessmentCategory", back_populates="questions")


# =========================
# Assessment
# =========================
class Assessment(Base, BaseMixin):

    __tablename__ = "assessments"

    org_id = Column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )

    framework_id = Column(
        ForeignKey("maturity_frameworks.id", ondelete="CASCADE"),
        nullable=False
    )

    status = Column(String(50), default="in_progress")

    organization = relationship("Organization", back_populates="assessments")
    framework = relationship("MaturityFramework")

    responses = relationship(
        "AssessmentResponse",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )

    scores = relationship(
        "MaturityScore",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )


# =========================
# Response
# =========================
class AssessmentResponse(Base, BaseMixin):

    __tablename__ = "assessment_responses"

    assessment_id = Column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False
    )

    question_id = Column(
        ForeignKey("assessment_questions.id", ondelete="CASCADE"),
        nullable=False
    )

    score = Column(Integer, nullable=True)
    text_response = Column(Text, nullable=True)

    assessment = relationship("Assessment", back_populates="responses")
    question = relationship("AssessmentQuestion")


# =========================
# Maturity Score
# =========================
class MaturityScore(Base, BaseMixin):

    __tablename__ = "maturity_scores"

    assessment_id = Column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False
    )

    category_id = Column(
        ForeignKey("assessment_categories.id", ondelete="CASCADE"),
        nullable=False
    )

    score = Column(Numeric(5, 2), nullable=False)
    level = Column(String(50), nullable=False)
    ai_summary = Column(Text, nullable=True)

    assessment = relationship("Assessment", back_populates="scores")