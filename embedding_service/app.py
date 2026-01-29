import logging

from fastapi import FastAPI

from service.blob_storage import BlobStorage
from service.embedding_service import EmbeddingService
from processor.document_processor import DocumentProcessor
from client.qdrant_vector_client import QdrantVectorClient
from router import embedding_router
from config.vars import (
    QDRANT_URL, 
    BLOB_STORAGE_PATH,
    SENTENCE_TRANSFORMER_MODEL,
)


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('httpcore.http11').setLevel(logging.WARNING)
logging.getLogger('httpcore.connection').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('anthropic').setLevel(logging.WARNING)
logging.getLogger('anthropic._base_client').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(title="Deep Research Embedding Service")

logger.info("Starting Deep Research Embedding Service initialization")
logger.info(f"Qdrant URL: {QDRANT_URL}")
logger.info(f"Model: {SENTENCE_TRANSFORMER_MODEL}")
logger.info(f"Blob Storage Path: {BLOB_STORAGE_PATH}")

embedding_service = EmbeddingService(model_name=SENTENCE_TRANSFORMER_MODEL)
vector_client = QdrantVectorClient(url=QDRANT_URL)
blob_storage = BlobStorage(storage_path=BLOB_STORAGE_PATH)
document_processor = DocumentProcessor(embedding_service=embedding_service)

logger.info("All services initialized successfully")

app.state.embedding_service = embedding_service
app.state.vector_client = vector_client
app.state.blob_storage = blob_storage
app.state.document_processor = document_processor

app.include_router(embedding_router.router)


@app.get("/health")
async def health():
    logger.debug("Health check requested")
    return {"status": "ok"}

