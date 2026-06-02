from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Enum

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.models.base import BaseMixin
from app.models.enums import UserRole


class User(Base, BaseMixin):

    __tablename__ = "users"

    name = Column(
        String(255),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        Enum(UserRole),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False
    )

    organization = relationship(
        "Organization",
        back_populates="users"
    )