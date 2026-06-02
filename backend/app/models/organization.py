from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseMixin


class Organization(Base, BaseMixin):

    __tablename__ = "organizations"

    name = Column(
        String(255),
        nullable=False,
        index=True
    )

    description = Column(
        String(1000),
        nullable=True
    )

    industry = Column(
        String(255),
        nullable=True
    )

    employee_count = Column(
        Integer,
        nullable=True
    )

    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan"
    )