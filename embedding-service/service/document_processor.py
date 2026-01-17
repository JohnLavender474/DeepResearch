import uuid

from typing import List, Dict
from unstructured.partition.auto import partition

from qdrant_client.models import PointStruct

from service.embedding_service import EmbeddingService
from model.chunk_metadata import ChunkMetadata


class DocumentProcessor:

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service


    def extract_text(self, file_path: str) -> str:
        elements = partition(filename=file_path)
        text = "\n\n".join([str(el) for el in elements])
        return text


    def chunk_text(self, text: str, chunk_size: int) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks


    def process_document(
        self,
        file_path: str,
        filename: str,
        metadata: Dict[str, str],
        chunk_size: int = 2000
    ) -> List[PointStruct]:
        text = self.extract_text(file_path)
        
        chunks = self.chunk_text(text, chunk_size)
        
        points = []
        for i, chunk in enumerate(chunks):
            vector = self.embedding_service.get_encoding(chunk)
            
            point_id = str(uuid.uuid4())
            
            chunk_metadata = ChunkMetadata(
                chunk_index=i,
                source_name=filename,
                content=chunk
            )
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=chunk_metadata.model_dump()
                )
            )
        
        return points
