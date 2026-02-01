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
) -> ProfileModel:  
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
        created_at=db_profile.created_at.isoformat(),
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
) -> list[ProfileModel]:
    return db.query(ProfileModel).all()
