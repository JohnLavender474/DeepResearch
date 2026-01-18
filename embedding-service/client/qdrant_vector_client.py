import logging

from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams
)


logger = logging.getLogger(__name__)


class QdrantVectorClient:

    def __init__(self, url: str):
        logger.info(f"Initializing QdrantVectorClient with URL: {url}")
        self.client = QdrantClient(url=url)
        logger.debug("QdrantVectorClient initialized successfully")


    def create_collection(
        self,
        collection_name: str,
        vector_size: int
    ):
        logger.info(f"Creating collection '{collection_name}' with vector size {vector_size}")
        client: QdrantClient = self.client
        try:
            client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
            )
            logger.info(f"Collection '{collection_name}' created successfully")
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            raise Exception(f"Failed to create collection: {e}")


    def upsert(
        self,
        collection_name: str,
        points: List[PointStruct]
    ):
        logger.debug(f"Upserting {len(points)} points to collection '{collection_name}'")
        client: QdrantClient = self.client
        try:
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.debug(f"Successfully upserted {len(points)} points to collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to upsert points to collection '{collection_name}': {e}")
            raise


    def collection_exists(self, collection_name: str) -> bool:
        logger.debug(f"Checking if collection '{collection_name}' exists")
        try:
            collections = self.client.get_collections()
            exists = any(
                collection.name == collection_name 
                for collection in collections.collections
            )
            logger.debug(
                f"Collection '{collection_name}' exists: {exists}"
            )
            return exists
        except Exception as e:
            logger.error(f"Failed to check collection existence: {e}")
            raise
        

    def get_collections(self) -> List[str]:
        logger.debug("Fetching all collections")
        try:
            response = self.client.get_collections()
            collection_names = [collection.name for collection in response.collections]
            logger.debug(f"Found {len(collection_names)} collections")
            return collection_names
        except Exception as e:
            logger.error(f"Failed to fetch collections: {e}")
            raise


    def delete_collection(self, collection_name: str) -> bool:
        logger.info(f"Deleting collection '{collection_name}'")
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            raise


    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        logger.debug(f"Searching collection '{collection_name}' with top_k={top_k}")
        client: QdrantClient = self.client
        try:
            hits = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k
            )
            results = [
                {
                    "id": h.id,
                    "score": h.score,
                    "metadata": h.payload
                } for h in hits
            ]
            logger.debug(f"Search returned {len(results)} results from collection '{collection_name}'")
            return results
        except Exception as e:
            logger.error(f"Search failed on collection '{collection_name}': {e}")
            raise

    
    def get_all_points(
        self,
        collection_name: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        logger.debug(
            f"Fetching all points from collection '{collection_name}' "
            f"with limit={limit}"
        )
        client: QdrantClient = self.client
        try:
            points = client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            results = [
                {
                    "id": point.id,
                    "payload": point.payload
                } 
                for point in points[0]
            ]
            logger.debug(
                f"Retrieved {len(results)} points from "
                f"collection '{collection_name}'"
            )
            return results
        except Exception as e:
            logger.error(
                f"Failed to fetch points from collection "
                f"'{collection_name}': {e}"
            )
            raise
