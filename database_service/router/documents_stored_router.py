from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from model.documents_stored import (
    DocumentsStoredCreate,
    DocumentsStoredResponse,
)
from service import documents_stored_service
from dependencies import get_db
import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/database",
    tags=["database"],
)


@router.post("/{profile_id}/documents-stored")
def create_document_stored(
    profile_id: str,
    document: DocumentsStoredCreate,
    db: Session = Depends(get_db),
) -> DocumentsStoredResponse:
    logger.info(
        f"Creating document stored entry: {document.filename} "
        f"for profile: {profile_id}"
    )

    created = documents_stored_service.create_document_stored(
        db=db,
        profile_id=profile_id,
        document=document,
    )

    return created


@router.delete("/{profile_id}/documents-stored/{filename}")
def delete_document_stored(
    filename: str,
    profile_id: str,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Deleting document stored entry: {filename} "
        f"for profile: {profile_id}"
    )

    success = documents_stored_service.delete_document_stored(
        db=db,
        filename=filename,
        profile_id=profile_id,
    )

    if not success:
        logger.warning(
            f"Document stored entry '{filename}' not found for profile "
            f"'{profile_id}'"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Document '{filename}' not found for profile '{profile_id}'",
        )

    return {"status": "ok", "filename": filename}


@router.get("/{profile_id}/documents-stored")
def get_documents_by_profile(
    profile_id: str,
    db: Session = Depends(get_db),
) -> list[DocumentsStoredResponse]:
    logger.info(f"Getting documents for profile: {profile_id}")

    documents = documents_stored_service.get_documents_by_profile(
        db=db,
        profile_id=profile_id,
    )

    return documents