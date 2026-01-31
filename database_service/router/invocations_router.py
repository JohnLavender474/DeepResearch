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
from service import invocations_service
from service import invocation_stop_requests_service
from dependencies import get_db

import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/database",
    tags=["database"],
)


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

    existing = invocations_service.get_invocation_by_id(
        db=db,
        invocation_id=invocation.invocation_id,
        profile_id=profile_id,
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Invocation already exists",
        )

    return invocations_service.create_invocation(
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
    invocation = invocations_service.get_invocation_by_id(
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
    limit: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    logger.info(
        f"Fetching invocations for profile {profile_id} "
        f"limit={limit})"
    )

    return invocations_service.get_invocations_by_profile_id(
        db=db,
        profile_id=profile_id,       
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

    updated = invocations_service.update_invocation(
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

    deleted = invocations_service.delete_invocation_by_id(
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
