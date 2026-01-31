import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from model.invocation_stop_request import (
    InvocationStopRequestCreate,
    InvocationStopRequestResponse,
)
from service import invocation_stop_requests_service
from dependencies import get_db


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/database",
    tags=["database"],
)


@router.post(
    "/invocation-stop-requests",
    response_model=InvocationStopRequestResponse,
)
def create_stop_request(
    stop_request: InvocationStopRequestCreate,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Creating stop request for invocation {stop_request.invocation_id}"
    )

    existing = invocation_stop_requests_service.get_stop_request_by_invocation_id(
        db=db,
        invocation_id=stop_request.invocation_id,
    )

    if existing:
        return existing

    return invocation_stop_requests_service.create_stop_request(
        db=db,
        invocation_id=stop_request.invocation_id,
    )


@router.get(
    "/invocation-stop-requests/{invocation_id}",
    response_model=InvocationStopRequestResponse,
)
def get_stop_request(
    invocation_id: str,
    db: Session = Depends(get_db),
):
    stop_request = invocation_stop_requests_service.get_stop_request_by_invocation_id(
        db=db,
        invocation_id=invocation_id,
    )

    if not stop_request:
        raise HTTPException(
            status_code=404,
            detail="Stop request not found",
        )

    return stop_request


@router.delete(
    "/invocation-stop-requests/{invocation_id}",
)
def delete_stop_request(
    invocation_id: str,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Deleting stop request for invocation {invocation_id}"
    )

    deleted = invocation_stop_requests_service.delete_stop_request_by_invocation_id(
        db=db,
        invocation_id=invocation_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Stop request not found",
        )

    return {
        "message": "Stop request deleted successfully"
    }
