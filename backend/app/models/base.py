import uuid

from datetime import UTC
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Boolean

from sqlalchemy.orm import declared_attr

from sqlalchemy.dialects.postgresql import UUID


class BaseMixin:

    __abstract__ = True

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        )

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC),
            nullable=False
        )

    @declared_attr
    def is_deleted(cls):
        return Column(
            Boolean,
            default=False,
            nullable=False
        )