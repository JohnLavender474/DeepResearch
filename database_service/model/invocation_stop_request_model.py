from datetime import datetime

from sqlalchemy import Column, String, DateTime

from model.base import Base


class InvocationStopRequestModel(Base):
    __tablename__ = "invocation_stop_requests"

    invocation_id = Column(
        String,
        primary_key=True,
    )
    created_at = Column(
        DateTime,
        nullable=False,
    )
    expires_at = Column(
        DateTime,
        nullable=False,
    )
