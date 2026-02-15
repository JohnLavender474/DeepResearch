from fastapi import HTTPException

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.vars import DATABASE_URL

import logging


logger = logging.getLogger(__name__)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connections before use to detect stale connections
    pool_recycle=300,  # Recycle connections after 5 minutes to prevent stale connections
    pool_size=5,  # Number of persistent connections to maintain in the pool
    max_overflow=10,  # Max temporary connections beyond pool_size (total: 15)
    pool_timeout=30,  # Seconds to wait for available connection before raising TimeoutError
    connect_args={
        "connect_timeout": 10,  # Max seconds to wait for initial Postgres connection
        "keepalives": 1,  # Enable TCP keepalive to detect broken connections
        "keepalives_idle": 30,  # Seconds before sending first keepalive probe
        "keepalives_interval": 10,  # Seconds between keepalive probes
        "keepalives_count": 5,  # Max failed keepalive probes before closing connection
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException:        
        raise
    except Exception as e:
        logger.error(f"Database session error: {e}")        
        raise
    finally:
        logger.debug("Closing database session")
        db.close()
