import tempfile
import os
import logging

from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    UploadFile,
    File,
    Form
)

from model.search_query import SearchQuery
from client.qdrant_vector_client import QdrantVectorClient
from service.embedding_service import EmbeddingService
from processor.document_processor import DocumentProcessor


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/embedding", tags=["embedding"])


@router.get("/collections")
async def list_collections(request: Request):
    logger.info("Listing all collections")
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    collections = vector_client.get_collections()
    logger.info(f"Found {len(collections)} collections")
    return {"collections": collections}


@router.get("/collections/{collection_name}")
async def collection_exists(collection_name: str, request: Request):
    logger.info(f"Checking if collection '{collection_name}' exists")
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    exists = vector_client.collection_exists(collection_name)
    logger.info(f"Collection '{collection_name}' exists: {exists}")
    return {"exists": exists}


@router.post("/collections/{collection_name}")
async def create_collection(collection_name: str, request: Request):
    logger.info(f"Create collection request for '{collection_name}'")
    embedding_service: EmbeddingService = (
        request.app.state.embedding_service
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )

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


@router.get("/collections/{collection_name}/documents")
async def get_documents(
    collection_name: str,
    request: Request,
    limit: int = 100
):
    logger.info(
        f"Get documents request for collection '{collection_name}' "
        f"with limit={limit}"
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    
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


@router.post("/collections/{collection_name}/upload")
async def upload_document(
    request: Request,
    collection_name: str,
    file: UploadFile = File(...),
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

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(file.filename)[1]
    ) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        logger.debug(f"Processing document: {file.filename}")
        points = document_processor.process_document(
            file_path=tmp_path,
            filename=file.filename,
        )
        logger.info(f"Document processed into {len(points)} chunks")

        batch_size = 64
        for i in range(0, len(points), batch_size):
            logger.debug(f"Upserting batch {i // batch_size + 1}")
            vector_client.upsert(
                collection_name,
                points[i : i + batch_size]
            )

        logger.info(f"Document '{file.filename}' uploaded and indexed to collection '{collection_name}'")
        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_indexed": len(points)
        }

    except Exception as e:
        logger.error(f"Failed to upload document '{file.filename}': {e}")
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
