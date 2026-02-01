from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

from model.base import Base


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    profile_id = Column(String, ForeignKey("profiles.id"), nullable=False)
    title = Column(String, nullable=True)
    chat_turns = Column(ARRAY(String), nullable=False, default=[])
    created_at = Column(
        DateTime,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
    )
