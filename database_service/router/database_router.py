from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from model.invocation import (
    InvocationCreate,
    InvocationUpdate,
    InvocationResponse,
)
from service import database_service

import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/database",
    tags=["database"],
)


def get_db():
    from app import SessionLocal
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/{profile_id}/invocations",
    response_model=InvocationResponse,
)
def create_invocation(
    profile_id: str,
    invocation: InvocationCreate,
    db: Session = Depends(get_db),
):
    if invocation.profile_id != profile_id:
        raise HTTPException(
            status_code=400,
            detail="Profile ID in URL does not match profile ID in request body",
        )
    
    logger.info(
        f"Creating invocation {invocation.invocation_id} "
        f"for profile {profile_id}"
    )
    
    existing = database_service.get_invocation(
        db=db,
        invocation_id=invocation.invocation_id,
        profile_id=profile_id,
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Invocation already exists",
        )
    
    return database_service.create_invocation(
        db=db,
        invocation=invocation,
        profile_id=profile_id,
    )


@router.get(
    "/{profile_id}/invocations/{invocation_id}",
    response_model=InvocationResponse,
)
def get_invocation(
    profile_id: str,
    invocation_id: str,
    db: Session = Depends(get_db),
):
    invocation = database_service.get_invocation(
        db=db,
        invocation_id=invocation_id,
        profile_id=profile_id,
    )
    
    if not invocation:
        raise HTTPException(
            status_code=404,
            detail="Invocation not found",
        )
    
    return invocation


@router.get(
    "/{profile_id}/invocations",
    response_model=list[InvocationResponse],
)
def get_invocations(
    profile_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    logger.info(
        f"Fetching invocations for profile {profile_id} "
        f"(skip={skip}, limit={limit})"
    )
    
    return database_service.get_invocations(
        db=db,
        profile_id=profile_id,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{profile_id}/invocations/{invocation_id}",
    response_model=InvocationResponse,
)
def update_invocation(
    profile_id: str,
    invocation_id: str,
    invocation_update: InvocationUpdate,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Updating invocation {invocation_id} for profile {profile_id}"
    )
    
    updated = database_service.update_invocation(
        db=db,
        invocation_id=invocation_id,
        invocation_update=invocation_update,
        profile_id=profile_id,
    )
    
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Invocation not found",
        )
    
    return updated


@router.post(
    "/{profile_id}/invocations/{invocation_id}/stop",
    response_model=InvocationResponse,
)
def request_stop_invocation(
    profile_id: str,
    invocation_id: str,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Requesting stop for invocation {invocation_id} for profile {profile_id}"
    )
    
    updated = database_service.update_invocation(
        db=db,
        invocation_id=invocation_id,
        invocation_update=InvocationUpdate(status="stop_requested"),
        profile_id=profile_id,
    )
    
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Invocation not found",
        )
    
    return updated


@router.delete(
    "/{profile_id}/invocations/{invocation_id}",
)
def delete_invocation(
    profile_id: str,
    invocation_id: str,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Deleting invocation {invocation_id} for profile {profile_id}"
    )
    
    deleted = database_service.delete_invocation(
        db=db,
        invocation_id=invocation_id,
        profile_id=profile_id,
    )
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Invocation not found",
        )
    
    return {"message": "Invocation deleted successfully"}
