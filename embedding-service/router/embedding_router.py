import tempfile
import os
import json

from typing import List

from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    UploadFile,
    File,
    Form
)

from model.search_query import SearchQuery
from client.qdrant_client import QdrantVectorClient
from service.embedding_service import EmbeddingService
from service.document_processor import DocumentProcessor


router = APIRouter(prefix="/api/embedding", tags=["embedding"])


@router.post("/collections/{collection_name}")
async def create_collection(collection_name: str, request: Request):    
    embedding_service: EmbeddingService = (
        request.app.state.embedding_service
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    
    if vector_client.collection_exists(collection_name):
        raise HTTPException(
            status_code=409,
            detail=f"Collection '{collection_name}' already exists"
        )
    
    vector_size = embedding_service.get_dimension()
    vector_client.create_collection(collection_name, vector_size)
    
    return {
        "status": "ok",
        "collection": collection_name,
        "vector_size": vector_size
    }


@router.post("/collections/{collection_name}/upload")
async def upload_document(
    collection_name: str,
    file: UploadFile = File(...),
    metadata: str = Form("{}"),
    request: Request = None
):    
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    document_processor: DocumentProcessor = (
        request.app.state.document_processor
    )
    
    if not vector_client.collection_exists(collection_name):
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_name}' does not exist"
        )
    
    metadata_dict = json.loads(metadata)
    
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(file.filename)[1]
    ) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        points = document_processor.process_document(
            file_path=tmp_path,
            filename=file.filename,
            metadata=metadata_dict
        )
        
        batch_size = 64
        for i in range(0, len(points), batch_size):
            vector_client.upsert(
                collection_name,
                points[i : i + batch_size]
            )
        
        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_indexed": len(points)
        }
    
    finally:
        os.unlink(tmp_path)


@router.post("/collections/{collection_name}/search")
async def search(
    collection_name: str,
    query: SearchQuery,
    request: Request
):
    embedding_service: EmbeddingService = (
        request.app.state.embedding_service
    )
    vector_client: QdrantVectorClient = (
        request.app.state.vector_client
    )
    
    if not vector_client.collection_exists(collection_name):
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_name}' does not exist"
        )
    
    query_vector = embedding_service.get_encoding(query.query)
    
    results = vector_client.search(
        collection_name,
        query_vector,
        top_k=query.top_k
    )
    
    return {"results": results}
