import logging

from fastapi import FastAPI

from service.blob_storage import BlobStorage
from router import storage_router
from config.vars import BLOB_STORAGE_PATH


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('httpcore.http11').setLevel(logging.WARNING)
logging.getLogger('httpcore.connection').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(title="Deep Research Storage Service")

logger.info("Starting Deep Research Storage Service initialization")
logger.info(f"Blob Storage Path: {BLOB_STORAGE_PATH}")

blob_storage = BlobStorage(storage_path=BLOB_STORAGE_PATH)

logger.info("Storage service initialized successfully")

app.state.blob_storage = blob_storage

app.include_router(storage_router.router)


@app.get("/health")
async def health():
    logger.debug("Health check requested")
    return {"status": "ok"}
