import logging
import tempfile
import os
import httpx

from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.responses import Response

from service.blob_storage import BlobStorage
from config.vars import DATABASE_SERVICE_URL, EMBEDDING_SERVICE_URL


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/storage", tags=["storage"])


@router.get("/collections/{collection_name}/documents")
async def get_document_names(collection_name: str, request: Request):
    logger.info(
        f"Get document names request for collection '{collection_name}'"
    )
    blob_storage: BlobStorage = request.app.state.blob_storage

    try:
        documents = blob_storage.list_blobs(
            collection_name=collection_name
        )
        logger.info(
            f"Found {len(documents)} documents in collection "
            f"'{collection_name}'"
        )
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Failed to get document names: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get document names: {e}"
        )


@router.post("/collections/{collection_name}/blobs")
async def upload_blob(
    collection_name: str,
    file: UploadFile = File(...),
    request: Request = None
):
    logger.info(
        f"Upload blob request for collection '{collection_name}', "
        f"filename: {file.filename}"
    )
    blob_storage: BlobStorage = request.app.state.blob_storage

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        stored_path = blob_storage.store_blob(
            collection_name=collection_name,
            filename=file.filename,
            file_path=temp_file_path
        )

        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{DATABASE_SERVICE_URL}/documents-stored/{collection_name}",
                    json={
                        "filename": file.filename,                        
                    },
                )
            except Exception as e:
                logger.error(
                    f"Failed to create document stored entry for "
                    f"'{file.filename}' in profile '{collection_name}': {e}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Failed to create document stored entry for "
                        f"'{file.filename}' in profile '{collection_name}': {e}"
                    )
                )

        logger.info(
            f"Uploaded blob: {file.filename} to collection '{collection_name}'"
        )
        return {
            "status": "ok",
            "filename": file.filename,
            "collection": collection_name,
            "path": stored_path
        }
    except Exception as e:
        logger.error(f"Failed to upload blob: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload blob: {e}"
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.get("/collections/{collection_name}/blobs/{filename}")
async def get_blob(
    collection_name: str,
    filename: str,
    request: Request
):
    logger.info(
        f"Get blob request for collection '{collection_name}', "
        f"filename: {filename}"
    )
    blob_storage: BlobStorage = request.app.state.blob_storage

    try:
        blob_content = blob_storage.retrieve_blob(
            collection_name=collection_name,
            filename=filename
        )

        if blob_content is None:
            logger.error(f"Blob not found: {filename}")
            raise HTTPException(
                status_code=404,
                detail=f"Blob '{filename}' not found"
            )

        logger.info(f"Retrieved blob: {filename}")
        return Response(
            content=blob_content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve blob: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve blob: {e}"
        )


@router.delete("/collections/{collection_name}/blobs/{filename}")
async def delete_blob(
    collection_name: str,
    filename: str,
    request: Request
):
    logger.info(
        f"Delete blob request for collection '{collection_name}', "
        f"filename: {filename}"
    )
    blob_storage: BlobStorage = request.app.state.blob_storage

    try:
        success = blob_storage.delete_blob(
            collection_name=collection_name,
            filename=filename
        )

        if not success:
            logger.error(f"Blob not found: {filename}")
            raise HTTPException(
                status_code=404,
                detail=f"Blob '{filename}' not found"
            )

        async with httpx.AsyncClient() as client:
            try:
                await client.delete(
                    f"{DATABASE_SERVICE_URL}/documents-stored/{collection_name}/{filename}",
                )
            except httpx.HTTPStatusError as http_exc:
                if http_exc.response.status_code == 404:
                    logger.warning(
                        f"Document stored entry '{filename}' not found for profile "
                        f"'{collection_name}' in database service"
                    )
                else:
                    logger.error(
                        f"Failed to delete document stored entry for "
                        f"'{filename}' in profile '{collection_name}': {http_exc}"
                    )
                    raise HTTPException(
                        status_code=500,
                        detail=(
                            f"Failed to delete document stored entry for "
                            f"'{filename}' in profile '{collection_name}': {http_exc}"
                        )
                    )
            except Exception as e:
                logger.error(
                    f"Failed to delete document stored entry for "
                    f"'{filename}' in profile '{collection_name}': {e}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Failed to delete document stored entry for "
                        f"'{filename}' in profile '{collection_name}': {e}"
                    )
                )

        logger.info(f"Deleted blob: {filename}")
        return {
            "status": "ok",
            "filename": filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete blob: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete blob: {e}"
        )