import logging

from fastapi import FastAPI

from router.process_selection_router import process_selection_router

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Deep Research Graph Service")

app.include_router(process_selection_router)

logger.info("Starting Deep Research Graph Service initialization")
logger.info("Graph service initialized successfully")


@app.get("/health")
async def health():
    logger.debug("Health check requested")
    return {"status": "ok"}
