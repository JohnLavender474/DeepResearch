import uuid
import logging
from typing import List

from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from model.document_insertion import TextInsertion


logger = logging.getLogger(__name__)


DEFAULT_EMBEDDING_DIMENSION = 768


class EmbeddingService:

    def __init__(self, model_name: str):
        logger.info(f"Initializing EmbeddingService with model: {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension() or DEFAULT_EMBEDDING_DIMENSION
        logger.info(f"EmbeddingService initialized, embedding dimension: {self.dim}")


    def get_encoding(self, text: str) -> List[float]:
        logger.debug(f"Encoding text of length {len(text)}")
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()


    def get_encoding_for_batch(self, texts: List[str]) -> List[List[float]]:
        logger.debug(f"Encoding batch of {len(texts)} texts")
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


    def get_dimension(self) -> int:        
        return self.dim


    def text_to_point(self, text_insertion: TextInsertion) -> PointStruct:
        vector = self.get_encoding(text_insertion.content)
        
        point_id = str(uuid.uuid4())
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=text_insertion.metadata
        )
        
        return point


    def texts_to_points(
        self,
        text_insertions: List[TextInsertion]
    ) -> List[PointStruct]:
        points = []
        for text_insertion in text_insertions:
            point = self.text_to_point(text_insertion)
            points.append(point)
        
        return points
