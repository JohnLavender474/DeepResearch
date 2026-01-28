import logging

from fastapi import FastAPI

from router.process_selection_router import process_selection_router
from router.simple_process_router import simple_process_router
from router.parallel_synthesis_router import router as parallel_synthesis_router

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Deep Research Graph Service")

app.include_router(process_selection_router)
app.include_router(simple_process_router)
app.include_router(parallel_synthesis_router)

logger.info("Starting Deep Research Graph Service initialization")
logger.info("Graph service initialized successfully")


@app.get("/health")
async def health():
    logger.debug("Health check requested")
    return {"status": "ok"}
