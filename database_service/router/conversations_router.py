from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from model.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
)
from service import conversations_service
from dependencies import get_db

import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/database",
    tags=["database"],
)


@router.post(
    "/{profile_id}/conversations",
    response_model=ConversationResponse,
)
def create_conversation(
    profile_id: str,
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
):
    if conversation.profile_id != profile_id:
        raise HTTPException(
            status_code=400,
            detail="Profile ID in URL does not match profile ID in request body",
        )

    logger.info(
        f"Creating conversation {conversation.id} "
        f"for profile {profile_id}"
    )

    return conversations_service.create_conversation(
        db=db,
        conversation=conversation,
        profile_id=profile_id,
    )


@router.get(
    "/{profile_id}/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    profile_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
):
    conversation = conversations_service.get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        profile_id=profile_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation


@router.get(
    "/{profile_id}/conversations",
    response_model=list[ConversationResponse],
)
def get_conversations(
    profile_id: str,
    limit: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    logger.info(
        f"Fetching conversations for profile {profile_id} "
        f"limit={limit}"
    )

    return conversations_service.get_conversations_by_profile_id(
        db=db,
        profile_id=profile_id,
        limit=limit,
    )


@router.patch(
    "/{profile_id}/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    profile_id: str,
    conversation_id: str,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Updating conversation {conversation_id} for profile {profile_id}"
    )

    updated = conversations_service.update_conversation(
        db=db,
        conversation_id=conversation_id,
        conversation_update=conversation_update,
        profile_id=profile_id,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return updated


@router.delete(
    "/{profile_id}/conversations/{conversation_id}",
)
def delete_conversation(
    profile_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Deleting conversation {conversation_id} for profile {profile_id}"
    )

    deleted = conversations_service.delete_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        profile_id=profile_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {"message": "Conversation deleted successfully"}
