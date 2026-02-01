from fastapi import (
    APIRouter,
    Depends,
    HTTPException,    
)
from sqlalchemy.orm import Session

from model.profile import ProfileCreate, ProfileResponse
from service import profiles_service
from dependencies import get_db

import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/database",
    tags=["database"],
)


@router.post("/profiles")
def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(get_db),
) -> ProfileResponse:
    if profiles_service.exists_profile_by_id(db, profile.id):
        raise HTTPException(
            status_code=400,
            detail=f"Profile with ID {profile.id} already exists."
        )

    logger.info(f"Creating profile: {profile.id}")

    created = profiles_service.create_profile(
        db=db,
        profile=profile,
    )

    return ProfileResponse(
        id=created.id,
        created_at=str(created.created_at),
    )


@router.get("/profiles")
def get_profiles(
    db: Session = Depends(get_db),
) -> list[ProfileResponse]:
    logger.info("Fetching all profiles")

    profiles = profiles_service.get_all_profiles(
        db=db,
    )

    return profiles



