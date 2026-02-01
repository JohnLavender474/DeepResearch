from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from model.documents_stored import (
    DocumentsStoredCreate,
    DocumentsStoredResponse,
)
from model.documents_stored_model import DocumentsStoredModel


def create_document_stored(
    db: Session,
    profile_id: str,
    document: DocumentsStoredCreate,
) -> DocumentsStoredResponse:
    uploaded_at = datetime.now(timezone.utc)

    db_document = DocumentsStoredModel(
        id=str(uuid.uuid4()),
        filename=document.filename,
        profile_id=profile_id,
        uploaded_at=uploaded_at,
    )
    db.add(db_document)
    
    db.commit()
    db.refresh(db_document)

    return DocumentsStoredResponse(
        id=db_document.id,
        filename=db_document.filename,
        profile_id=db_document.profile_id,
        uploaded_at=str(db_document.uploaded_at),
    )


def delete_document_stored(
    db: Session,
    filename: str,
    profile_id: str,
) -> bool:
    result = db.query(DocumentsStoredModel).filter(
        DocumentsStoredModel.filename == filename,
        DocumentsStoredModel.profile_id == profile_id,
    ).delete()

    db.commit()
    return result > 0


def get_documents_by_profile(
    db: Session,
    profile_id: str,
) -> list[DocumentsStoredResponse]:
    documents = db.query(DocumentsStoredModel).filter(
        DocumentsStoredModel.profile_id == profile_id
    ).all()

    return [
        DocumentsStoredResponse(
            id=doc.id,
            filename=doc.filename,
            profile_id=doc.profile_id,
            uploaded_at=str(doc.uploaded_at),
        )
        for doc in documents
    ]
