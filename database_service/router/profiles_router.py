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


PROFILE_IDS_NOT_ALLOWED = [
    "conversations",
]


@router.post("/profiles")
def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(get_db),
) -> ProfileResponse:
    if profile.id in PROFILE_IDS_NOT_ALLOWED:
        logger.warning(f"Attempt to create profile with reserved ID '{profile.id}'")
        raise HTTPException(
            status_code=400,
            detail=f"Profile ID '{profile.id}' is reserved and cannot be used"
        )

    if profiles_service.exists_profile_by_id(
        db=db,
        profile_id=profile.id,
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Profile with ID {profile.id} already exists."
        )

    logger.info(f"Creating profile: {profile.id}")

    created = profiles_service.create_profile(
        db=db,
        profile=profile,
    )

    return created


@router.get("/profiles")
def get_profiles(
    db: Session = Depends(get_db),
) -> list[ProfileResponse]:
    logger.info("Fetching all profiles")

    profiles = profiles_service.get_all_profiles(
        db=db,
    )

    return profiles



