from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Date, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.database import Base
from app.models.base import BaseMixin

class Project(Base, BaseMixin):
    __tablename__ = "projects"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="on_track")  # on_track, at_risk, delayed, completed
    health_score = Column(Numeric(5, 2), default=100.0)
    budget = Column(Numeric(15, 2), default=0.0)
    budget_used = Column(Numeric(15, 2), default=0.0)
    start_date = Column(Date, nullable=True)
    target_end_date = Column(Date, nullable=True)
    team_size = Column(Integer, default=1)

    organization = relationship("Organization")
    risks = relationship("ProjectRisk", back_populates="project", cascade="all, delete-orphan")
    resources = relationship("ProjectResource", back_populates="project", cascade="all, delete-orphan")
    sprints = relationship("SprintData", back_populates="project", cascade="all, delete-orphan")

class ProjectRisk(Base, BaseMixin):
    __tablename__ = "project_risks"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), default="medium")  # high, medium, low

    project = relationship("Project", back_populates="risks")

class ProjectResource(Base, BaseMixin):
    __tablename__ = "project_resources"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    resource_name = Column(String(255), nullable=False)
    allocation_percent = Column(Integer, default=100)
    role = Column(String(100), nullable=True)
    skills = Column(String(255), nullable=True)

    project = relationship("Project", back_populates="resources")

class SprintData(Base, BaseMixin):
    __tablename__ = "sprint_data"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    sprint_number = Column(Integer, nullable=False)
    velocity = Column(Integer, default=0)
    completion_rate = Column(Numeric(5, 2), default=100.0)

    project = relationship("Project", back_populates="sprints")

class Conversation(Base, BaseMixin):
    __tablename__ = "conversations"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Discussion")

    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")

class AIMessage(Base, BaseMixin):
    __tablename__ = "ai_messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    agent_used = Column(String(100), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")

class AIRecommendation(Base, BaseMixin):
    __tablename__ = "ai_recommendations"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(100), nullable=False)  # risk, resource, timeline
    priority = Column(String(20), default="medium")  # high, medium, low
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action_items = Column(JSON, nullable=True)  # Store actionable items as list
