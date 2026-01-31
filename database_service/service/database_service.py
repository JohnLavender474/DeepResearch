from typing import Optional

from sqlalchemy.orm import Session

from model.db_models import InvocationModel
from model.invocation import (
    InvocationCreate,
    InvocationUpdate,
)


def create_invocation(
    db: Session,
    profile_id: str,
    invocation: InvocationCreate,
) -> InvocationModel:
    db_invocation = InvocationModel(
        invocation_id=invocation.invocation_id,
        profile_id=profile_id,
        user_query=invocation.user_query,
        status=invocation.status,
        graph_state=invocation.graph_state,
    )
    db.add(db_invocation)
    db.commit()
    db.refresh(db_invocation)
    return db_invocation


def get_invocation(
    db: Session,
    invocation_id: str,
    profile_id: str,
) -> Optional[InvocationModel]:
    return db.query(InvocationModel).filter(
        InvocationModel.invocation_id == invocation_id,
        InvocationModel.profile_id == profile_id,
    ).first()


def get_invocations(
    db: Session,
    profile_id: str,
    skip: int = 0,
    limit: int = 100,
) -> list[InvocationModel]:
    return db.query(InvocationModel).filter(
        InvocationModel.profile_id == profile_id
    ).order_by(
        InvocationModel.created_at.desc()
    ).offset(skip).limit(limit).all()


def update_invocation(
    db: Session,
    invocation_id: str,
    invocation_update: InvocationUpdate,
    profile_id: str,
) -> Optional[InvocationModel]:
    db_invocation = get_invocation(
        db=db,
        invocation_id=invocation_id,
        profile_id=profile_id,
    )
    
    if not db_invocation:
        return None
    
    if invocation_update.status is not None:
        db_invocation.status = invocation_update.status
    
    if invocation_update.graph_state is not None:
        db_invocation.graph_state = invocation_update.graph_state
    
    db.commit()
    db.refresh(db_invocation)
    return db_invocation


def delete_invocation(
    db: Session,
    invocation_id: str,
    profile_id: str,
) -> bool:
    db_invocation = get_invocation(
        db=db,
        invocation_id=invocation_id,
        profile_id=profile_id,
    )
    
    if not db_invocation:
        return False
    
    db.delete(db_invocation)
    db.commit()
    return True
