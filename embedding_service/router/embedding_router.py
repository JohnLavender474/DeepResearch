import tempfile
import os
import logging
import json
import httpx

from typing import Any, Optional
from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from model.search_query import SearchQuery
from client.qdrant_vector_client import QdrantVectorClient
from service.embedding_service import EmbeddingService
from processor.document_processor import DocumentProcessor
from config.vars import DATABASE_SERVICE_URL


RESERVED_COLLECTION_NAMES = [
    "conversations",
]



logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/embeddings", tags=["embedding"])


@router.get("/collections")
async def list_collections(request: Request):
    logger.info("Listing all collections")
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    try:
        collections = vector_client.get_collections()
        logger.info(f"Found {len(collections)} collections")
        return {"collections": collections}
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list collections: {e}"
        )


@router.get("/collections/{collection_name}")
async def collection_exists(collection_name: str, request: Request):
    logger.info(f"Checking if collection '{collection_name}' exists")
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )

    try:
        exists = vector_client.collection_exists(collection_name)
        logger.info(f"Collection '{collection_name}' exists: {exists}")
        return {"exists": exists}
    except Exception as e:
        logger.error(f"Failed to check collection existence: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check collection existence: {e}"
        )


@router.post("/collections/{collection_name}")
async def create_collection(collection_name: str, request: Request):
    if collection_name in RESERVED_COLLECTION_NAMES:
        logger.warning(f"Attempt to create collection with reserved name '{collection_name}'")
        raise HTTPException(
            status_code=400,
            detail=f"Collection name '{collection_name}' is reserved and cannot be used"
        )

    logger.info(f"Create collection request for '{collection_name}'")
    embedding_service: EmbeddingService = (
        request.app.state.embedding_service
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )

    try:
        if vector_client.collection_exists(collection_name):
            logger.warning(f"Collection '{collection_name}' already exists")
            raise HTTPException(
                status_code=409,
                detail=f"Collection '{collection_name}' already exists"
            )

        vector_size = embedding_service.get_dimension()
        vector_client.create_collection(collection_name, vector_size)

        logger.info(f"Collection '{collection_name}' created successfully")
        return {
            "status": "ok",
            "collection": collection_name,
            "vector_size": vector_size
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create collection: {e}"
        )
    

@router.get("/collections/{collection_name}/documents")
async def get_documents(
    collection_name: str,
    request: Request,
    limit: Optional[int] = None
):
    logger.info(
        f"Get documents request for collection '{collection_name}' "
        f"with limit={limit}"
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )

    try:
        if not vector_client.collection_exists(collection_name=collection_name):
            logger.error(f"Collection '{collection_name}' does not exist")
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' does not exist"
            )

        documents = vector_client.get_all_points(
            collection_name=collection_name,
            limit=limit
        )

        logger.info(
            f"Retrieved {len(documents)} documents from "
            f"collection '{collection_name}'"
        )
        return {
            "collection": collection_name,
            "documents": documents,
            "count": len(documents)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {e}"
        )


@router.post("/collections/{collection_name}/upload")
async def upload_document(
    request: Request,
    collection_name: str,
    file: UploadFile = File(...),
    custom_metadata: dict[str, Any] = Form(default={})
):
    logger.info(f"Upload document request for collection '{collection_name}', file: {file.filename}")
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    document_processor: DocumentProcessor = (
        request.app.state.document_processor
    )

    if not vector_client.collection_exists(collection_name):
        logger.error(f"Collection '{collection_name}' does not exist")
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_name}' does not exist"
        )

    existing_count = vector_client.count_points_by_source(
        collection_name,
        file.filename
    )
    if existing_count > 0:
        logger.warning(
            f"Document '{file.filename}' already exists in "
            f"collection '{collection_name}'"
        )
        raise HTTPException(
            status_code=409,
            detail=(
                f"Document '{file.filename}' already exists in "
                f"collection '{collection_name}'. Use PUT to replace it."
            )
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(file.filename)[1]
    ) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        logger.debug(f"Processing document: {file.filename}")
        
        batch_size = 64
        batch = []
        total_chunks = 0
        all_points = []
        
        for point in document_processor.process_document(
            file_path=tmp_path,
            filename=file.filename,
            custom_metadata=custom_metadata
        ):
            batch.append(point)
            all_points.append(point)
            total_chunks += 1
            
            if len(batch) >= batch_size:
                logger.debug(f"Upserting batch of {len(batch)} points")
                vector_client.upsert(collection_name, batch)
                batch = []
        
        if batch:
            logger.debug(f"Upserting final batch of {len(batch)} points")
            vector_client.upsert(collection_name, batch)
        
        logger.info(f"Document processed into {total_chunks} chunks")

        async with httpx.AsyncClient() as client:
            try:
                await client.put(
                    f"{DATABASE_SERVICE_URL}/documents-embedded",
                    json={
                        "filename": file.filename,
                        "points": json.dumps([point.model_dump() for point in all_points]),
                    },
                )
                logger.info(
                    f"Recorded embedded document '{file.filename}' "
                    f"in database service"
                )
            except httpx.HTTPStatusError as http_exc:
                if http_exc.response.status_code == 409:
                    logger.warning(
                        f"Embedded document '{file.filename}' already exists "
                        f"in database service"
                    )
                else:
                    raise
            except Exception as e:
                logger.error(f"Failed to record embedded document in database service: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to record embedded document in database service: {e}"
                )                

        logger.info(f"Document '{file.filename}' uploaded and indexed to collection '{collection_name}'")
        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_indexed": total_chunks
        }
    except Exception as e:
        logger.error(f"Failed to upload document '{file.filename}': {e}")
        raise
    finally:
        os.unlink(tmp_path)


@router.delete("/collections/{collection_name}/documents/{source_name}")
async def delete_document(
    collection_name: str,
    source_name: str,
    request: Request
):
    logger.info(
        f"Delete document request for collection '{collection_name}', "
        f"source_name: {source_name}"
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )

    try:
        if not vector_client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist")
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' does not exist"
            )

        logger.debug(
            f"Checking if document '{source_name}' exists "
            f"in collection '{collection_name}'"
        )
        existing_count = vector_client.count_points_by_source(
            collection_name,
            source_name
        )

        if existing_count == 0:
            logger.warning(
                f"No chunks found for source_name='{source_name}' "
                f"in collection '{collection_name}'"
            )
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No chunks found for source_name='{source_name}' "
                    f"in collection '{collection_name}'"
                )
            )

        logger.info(
            f"Deleting {existing_count} chunks for '{source_name}' "
            f"from collection '{collection_name}'"
        )
        deleted_count = vector_client.delete_points_by_source(
            collection_name,
            source_name
        )

        async with httpx.AsyncClient() as client:
            try:
                await client.delete(
                    f"{DATABASE_SERVICE_URL}/documents-embedded",
                    params={"filename": source_name},
                )
                logger.info(
                    f"Deleted embedded document entry '{source_name}' "
                    f"in database service"
                )
            except httpx.HTTPStatusError as http_exc:
                if http_exc.response.status_code == 404:
                    logger.warning(
                        f"Embedded document '{source_name}' not found in database service"
                    )
                else:
                    raise
            except Exception as e:
                logger.error(f"Failed to delete embedded document in database service: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete embedded document in database service: {e}"
                )

        logger.info(
            f"Successfully deleted {deleted_count} chunks "
            f"for source_name='{source_name}' "
            f"from collection '{collection_name}'"
        )
        return {
            "status": "ok",
            "source_name": source_name,
            "chunks_deleted": deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete document '{source_name}': {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {e}"
        )


@router.put("/collections/{collection_name}/upload")
async def replace_document(
    request: Request,
    collection_name: str,
    file: UploadFile = File(...),
    custom_metadata: dict[str, Any] = Form(default={})
):
    logger.info(f"Replace document request for collection '{collection_name}', file: {file.filename}")
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    document_processor: DocumentProcessor = (
        request.app.state.document_processor
    )

    try:
        if not vector_client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist")
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' does not exist"
            )

        logger.debug(f"Checking if document '{file.filename}' exists")
        existing_count = vector_client.count_points_by_source(
            collection_name,
            file.filename
        )

        if existing_count == 0:
            logger.warning(
                f"No existing chunks found for '{file.filename}' "
                f"in collection '{collection_name}'"
            )
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No existing chunks found for '{file.filename}'. "
                    f"Use POST to upload a new document."
                )
            )

        logger.info(
            f"Found {existing_count} existing chunks for '{file.filename}', "
            f"deleting them"
        )
        deleted_count = vector_client.delete_points_by_source(
            collection_name,
            file.filename
        )
        logger.info(f"Deleted {deleted_count} chunks")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check existing document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check existing document: {e}"
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(file.filename)[1]
    ) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        logger.debug(f"Processing document: {file.filename}")
        
        batch_size = 64
        batch = []
        total_chunks = 0
        all_points = []
        
        for point in document_processor.process_document(
            file_path=tmp_path,
            filename=file.filename,
            custom_metadata=custom_metadata
        ):
            batch.append(point)
            all_points.append(point)
            total_chunks += 1
            
            if len(batch) >= batch_size:
                logger.debug(f"Upserting batch of {len(batch)} points")
                vector_client.upsert(collection_name, batch)
                batch = []
        
        if batch:
            logger.debug(f"Upserting final batch of {len(batch)} points")
            vector_client.upsert(collection_name, batch)
        
        logger.info(f"Document processed into {total_chunks} chunks")

        async with httpx.AsyncClient() as client:
            try:
                await client.put(
                    f"{DATABASE_SERVICE_URL}/documents-embedded",
                    json={
                        "filename": file.filename,
                        "points": json.dumps([point.model_dump() for point in all_points]),
                    },
                )
            except Exception as e:
                logger.error(f"Failed to record embedded document in database service: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to record embedded document in database service: {e}"
                )

        logger.info(
            f"Document '{file.filename}' replaced in "
            f"collection '{collection_name}'"
        )
        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_replaced": existing_count,
            "chunks_indexed": total_chunks
        }

    except Exception as e:
        logger.error(f"Failed to replace document '{file.filename}': {e}")
        raise
    finally:
        os.unlink(tmp_path)


@router.post("/collections/{collection_name}/search")
async def search(
    collection_name: str,
    query: SearchQuery,
    request: Request
):
    logger.info(f"Search request for collection '{collection_name}', query: {query.query[:50]}..., top_k: {query.top_k}")
    embedding_service: EmbeddingService = (
        request.app.state.embedding_service
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )

    try:
        if not vector_client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist")
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' does not exist"
            )

        logger.debug("Encoding search query")
        query_vector = embedding_service.get_encoding(query.query)

        results = vector_client.search(
            collection_name,
            query_vector,
            top_k=query.top_k
        )

        logger.info(f"Search completed, found {len(results)} results")
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {e}"
        )


@router.patch("/collections/{collection_name}/documents/{source_name}/metadata")
async def update_document_metadata(
    collection_name: str,
    source_name: str,
    custom_metadata: dict[str, Any],
    request: Request
):
    logger.info(
        f"Update metadata request for collection '{collection_name}', "
        f"source_name: {source_name}"
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )

    try:
        if not vector_client.collection_exists(collection_name):
            logger.error(f"Collection '{collection_name}' does not exist")
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' does not exist"
            )

        logger.debug(
            f"Checking if document '{source_name}' exists "
            f"in collection '{collection_name}'"
        )
        existing_count = vector_client.count_points_by_source(
            collection_name,
            source_name
        )

        if existing_count == 0:
            logger.warning(
                f"No chunks found for source_name='{source_name}' "
                f"in collection '{collection_name}'"
            )
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No chunks found for source_name='{source_name}' "
                    f"in collection '{collection_name}'"
                )
            )

        logger.info(
            f"Updating custom_metadata for {existing_count} chunks"
        )
        update_result = vector_client.update_custom_metadata_by_source(
            collection_name,
            source_name,
            custom_metadata
        )

        logger.info(
            f"Successfully updated metadata for '{source_name}' "
            f"in collection '{collection_name}'"
        )
        return {
            "status": "ok",
            "source_name": source_name,
            "update_result": update_result,
            "custom_metadata": custom_metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update metadata for '{source_name}': {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update metadata: {e}"
        )
