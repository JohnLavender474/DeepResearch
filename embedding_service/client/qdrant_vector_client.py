import logging

from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams,
    Filter, 
    FieldCondition, 
    MatchValue,
    UpdateResult
)


logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 100000


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


    def clear_collection(self, collection_name: str) -> int:
        logger.info(f"Clearing all points from collection '{collection_name}'")
        try:
            count_before = self.client.count(
                collection_name=collection_name
            ).count

            if count_before > 0:
                self.client.delete(
                    collection_name=collection_name,
                    points_selector=Filter(must=[])
                )

            logger.info(
                f"Cleared {count_before} points from "
                f"collection '{collection_name}'"
            )
            return count_before
        except Exception as e:
            logger.error(
                f"Failed to clear collection '{collection_name}': {e}"
            )
            raise


    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        logger.debug(
            f"Searching collection '{collection_name}' " + 
            f"with top_k={top_k}"
        )
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
            logger.debug(
                f"Search returned {len(results)} results " + 
                f"from collection '{collection_name}'"
            )
            return results
        except Exception as e:
            logger.error(f"Search failed on collection '{collection_name}': {e}")
            raise

    
    def get_all_points(
        self,
        collection_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        logger.debug(
            f"Fetching all points from collection '{collection_name}' "
            f"with limit={limit}"
        )
        client: QdrantClient = self.client
        try:
            limit = limit if limit is not None else DEFAULT_LIMIT

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


    def count_points_by_source(
        self,
        collection_name: str,
        source_name: str
    ) -> int:
        logger.debug(
            f"Counting points in '{collection_name}' "
            f"with source_name='{source_name}'"
        )
        try:          
            count_result = self.client.count(
                collection_name=collection_name,
                count_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source_name",
                            match=MatchValue(value=source_name)
                        )
                    ]
                )
            )
            logger.debug(
                f"Found {count_result.count} points with "
                f"source_name='{source_name}'"
            )
            return count_result.count
        except Exception as e:
            logger.error(f"Failed to count points by source: {e}")
            raise

    
    def delete_points_by_source(
        self,
        collection_name: str,
        source_name: str
    ) -> int:
        logger.info(
            f"Deleting points from '{collection_name}' "
            f"with source_name='{source_name}'"
        )
        try:
            count_before = self.client.count(
                collection_name=collection_name,
                count_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source_name",
                            match=MatchValue(value=source_name)
                        )
                    ]
                )
            ).count

            self.client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="source_name",
                            match=MatchValue(value=source_name)
                        )
                    ]
                )
            )

            logger.info(
                f"Deleted {count_before} points " + 
                f"from '{collection_name}' " +
                f"with source_name='{source_name}'"
            )
            return count_before
        except Exception as e:
            logger.error(f"Failed to delete points by source: {e}")
            raise


    def update_custom_metadata_by_source(
        self,
        collection_name: str,
        source_name: str,
        custom_metadata: Dict[str, Any]
    ) -> UpdateResult:
        logger.info(
            f"Updating custom_metadata for points in '{collection_name}' "
            f"with source_name='{source_name}'"
        )
        try:
            update_result = self.client.set_payload(
                collection_name=collection_name,
                payload={"custom_metadata": custom_metadata},
                points=Filter(
                    must=[
                        FieldCondition(
                            key="source_name",
                            match=MatchValue(value=source_name)
                        )
                    ]
                )
            )
            logger.info(
                f"Updated custom_metadata in '{collection_name}' " + 
                f"with source_name='{source_name}'"
            )
            return update_result
        except Exception as e:
            logger.error(
                f"Failed to update custom_metadata by source: {e}"
            )
            raise
