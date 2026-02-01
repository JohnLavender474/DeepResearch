import uuid

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from model.conversation_model import ConversationModel
from model.conversation import (
    ConversationCreate,
    ConversationUpdate,
)


def create_conversation(
    db: Session,
    profile_id: str,
    conversation: ConversationCreate,
) -> ConversationModel:
    id = str(uuid.uuid4())

    now = datetime.now(timezone.utc)

    db_conversation = ConversationModel(
        id=id,
        profile_id=profile_id,
        title=conversation.title,
        chat_turns=conversation.chat_turns,
        created_at=now,
        updated_at=now,
    )

    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


def get_conversation_by_id(
    db: Session,
    conversation_id: str,
    profile_id: str,
) -> Optional[ConversationModel]:
    return db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id,
        ConversationModel.profile_id == profile_id,
    ).first()


def get_conversations_by_profile_id(
    db: Session,
    profile_id: str,
    limit: Optional[int] = None,
) -> list[ConversationModel]:
    query = db.query(ConversationModel).filter(
        ConversationModel.profile_id == profile_id
    ).order_by(
        ConversationModel.updated_at.desc()
    )

    if limit is not None:
        query = query.limit(limit)

    return query.all()


def update_conversation(
    db: Session,
    conversation_id: str,
    conversation_update: ConversationUpdate,
    profile_id: str,
) -> Optional[ConversationModel]:
    db_conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        profile_id=profile_id,
    )

    if not db_conversation:
        return None

    if conversation_update.title is not None:
        db_conversation.title = conversation_update.title

    if conversation_update.chat_turns is not None:
        db_conversation.chat_turns = conversation_update.chat_turns

    db_conversation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


def delete_conversation_by_id(
    db: Session,
    conversation_id: str,
    profile_id: str,
) -> bool:
    db_conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        profile_id=profile_id,
    )

    if not db_conversation:
        return False

    db.delete(db_conversation)
    db.commit()

    return True
