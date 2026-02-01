from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from model.invocation_stop_request_model import InvocationStopRequestModel


STOP_REQUEST_TTL_SECONDS = 3600


def create_stop_request(
    db: Session,
    invocation_id: str,
) -> InvocationStopRequestModel:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=STOP_REQUEST_TTL_SECONDS)

    db_stop_request = InvocationStopRequestModel(
        invocation_id=invocation_id,
        created_at=now,
        expires_at=expires_at,
    )

    db.add(db_stop_request)
    db.commit()
    db.refresh(db_stop_request)

    return db_stop_request


def get_stop_request_by_invocation_id(
    db: Session,
    invocation_id: str,
) -> Optional[InvocationStopRequestModel]:
    now = datetime.now(timezone.utc)

    return db.query(InvocationStopRequestModel).filter(
        InvocationStopRequestModel.invocation_id == invocation_id,
    ).first()


def delete_stop_request_by_invocation_id(
    db: Session,
    invocation_id: str,
) -> bool:
    db_stop_request = db.query(InvocationStopRequestModel).filter(
        InvocationStopRequestModel.invocation_id == invocation_id,
    ).first()

    if not db_stop_request:
        return False

    db.delete(db_stop_request)
    db.commit()

    return True


def delete_expired_stop_requests(
    db: Session,
) -> int:
    now = datetime.now(timezone.utc)

    result = db.query(InvocationStopRequestModel).filter(
        InvocationStopRequestModel.expires_at <= now,
    ).delete()

    db.commit()

    return result
