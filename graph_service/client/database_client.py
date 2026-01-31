import httpx

from typing import Optional

import logging


logger = logging.getLogger(__name__)


DATABASE_SERVICE_URL = "http://localhost:8003/api/database"


async def get_invocation(
    profile_id: str,
    invocation_id: str,
):
    url = f"{DATABASE_SERVICE_URL}/{profile_id}/invocations/{invocation_id}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url=url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(
            f"Failed to get invocation {invocation_id}: {str(e)}"
        )
        raise


async def create_invocation(
    profile_id: str,
    invocation_id: str,
    user_query: str,
    status: str = "running",
    graph_state: Optional[dict] = None,
):
    url = f"{DATABASE_SERVICE_URL}/{profile_id}/invocations"
    
    payload = {
        "invocation_id": invocation_id,
        "profile_id": profile_id,
        "user_query": user_query,
        "status": status,
        "graph_state": graph_state,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url=url,
                json=payload,
            )
            response.raise_for_status()
            logger.info(
                f"Created invocation {invocation_id} for profile {profile_id}"
            )
            return response.json()
    except Exception as e:
        logger.error(
            f"Failed to create invocation {invocation_id}: {str(e)}"
        )
        raise


async def update_invocation(
    profile_id: str,
    invocation_id: str,
    status: Optional[str] = None,
    graph_state: Optional[dict] = None,
):
    url = f"{DATABASE_SERVICE_URL}/{profile_id}/invocations/{invocation_id}"
    
    payload = {}
    
    if status is not None:
        payload["status"] = status
    
    if graph_state is not None:
        payload["graph_state"] = graph_state
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                url=url,
                json=payload,
            )
            response.raise_for_status()
            logger.debug(
                f"Updated invocation {invocation_id} for profile {profile_id}"
            )
            return response.json()
    except Exception as e:
        logger.error(
            f"Failed to update invocation {invocation_id}: {str(e)}"
        )
        raise
