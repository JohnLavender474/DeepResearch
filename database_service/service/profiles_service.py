from datetime import datetime, timezone

from sqlalchemy.orm import Session

from model.profile import (
    ProfileCreate, 
    ProfileResponse,
)
from model.profile_model import ProfileModel


def create_profile(
    db: Session,
    profile: ProfileCreate,
) -> ProfileResponse:
    created_at = datetime.now(timezone.utc)

    db_profile = ProfileModel(
        id=profile.id,
        created_at=created_at,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return ProfileResponse(
        id=db_profile.id,
        created_at=str(db_profile.created_at),
    )


def exists_profile_by_id(
    db: Session,
    profile_id: str,
) -> bool:
    return db.query(
        db.query(ProfileModel).filter(
            ProfileModel.id == profile_id
        ).exists()
    ).scalar()


def get_all_profiles(
    db: Session,
) -> list[ProfileResponse]:
    profiles = db.query(ProfileModel).all()

    return [
        ProfileResponse(
            id=profile.id,
            created_at=str(profile.created_at),
        )
        for profile in profiles
    ]
