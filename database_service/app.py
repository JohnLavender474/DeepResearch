import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.vars import DATABASE_URL
from model.base import Base
from service import invocation_stop_requests_service

from router.invocations_router import router as invocations_router
from router.profiles_router import router as profiles_router
from router.invocation_stop_requests_router import router as invocation_stop_requests_router
from router.conversations_router import router as conversations_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def create_tables():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


CLEANUP_INTERVAL_SECONDS = 300


async def cleanup_expired_stop_requests():
    while True:
        try:
            await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)

            db = SessionLocal()
            try:
                deleted_count = invocation_stop_requests_service.delete_expired_stop_requests(
                    db=db,
                )
                if deleted_count > 0:
                    logger.info(
                        f"Cleaned up {deleted_count} expired stop requests"
                    )
            finally:
                db.close()
        except asyncio.CancelledError:
            logger.info("Stop request cleanup task cancelled")
            break
        except Exception as e:
            logger.error(
                f"Error during stop request cleanup: {str(e)}"
            )


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting up Database Service...")

    logger.debug(f"Creating tables with DATABASE_URL: {DATABASE_URL}")
    create_tables()
    logger.info("Tables created.")

    cleanup_task = asyncio.create_task(cleanup_expired_stop_requests())

    yield

    logger.info("Shutting down Database Service...")

    cleanup_task.cancel()

    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Database Service",
    description=(
        "Database service for managing graph " 
        "invocations and state",
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(invocations_router)
app.include_router(profiles_router)
app.include_router(invocation_stop_requests_router)
app.include_router(conversations_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
    )
