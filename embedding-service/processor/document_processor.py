import uuid
import logging

from typing import List

from pypdf import PdfReader
from qdrant_client.models import PointStruct

from service.embedding_service import EmbeddingService
from model.chunk_metadata import ChunkMetadata


logger = logging.getLogger(__name__)


class DocumentProcessor:

    def __init__(self, embedding_service: EmbeddingService):
        logger.info("Initializing DocumentProcessor")
        self.embedding_service = embedding_service


    def extract_text(self, file_path: str) -> str:
        logger.debug(f"Extracting text from {file_path}")
        if file_path.endswith('.pdf'):
            return self._extract_pdf(file_path)
        elif file_path.endswith('.txt'):
            return self._extract_text_file(file_path)
        else:
            logger.error(f"Unsupported file format for {file_path}")
            raise ValueError(
                f"Unsupported file format. Supported: .pdf, .txt"
            )


    def _extract_pdf(self, file_path: str) -> str:
        logger.debug(f"Extracting text from PDF: {file_path}")
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.debug(f"Extracted {len(text)} characters from PDF")
        return text


    def _extract_text_file(self, file_path: str) -> str:
        logger.debug(f"Extracting text from file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            logger.debug(f"Extracted {len(text)} characters from text file")
            return text


    def chunk_text(
        self,
        text: str,
        chunk_size: int
    ) -> List[str]:
        logger.debug(f"Chunking text of length {len(text)} with chunk_size {chunk_size}")
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            word_size = len(word) + 1
            if (
                current_size + word_size > chunk_size and
                len(current_chunk) != 0
            ):
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        logger.debug(f"Created {len(chunks)} chunks")
        return chunks


    def process_document(
        self,
        file_path: str,
        filename: str,
        chunk_size: int = 2000,
        custom_metadata: dict[str, any] = {}
    ) -> List[PointStruct]:
        logger.info(f"Processing document: {filename}")
        text = self.extract_text(file_path)

        chunks = self.chunk_text(text, chunk_size)
        logger.info(f"Document '{filename}' split into {len(chunks)} chunks")

        points = []
        for i, chunk in enumerate(chunks):
            vector = self.embedding_service.get_encoding(chunk)

            point_id = str(uuid.uuid4())

            chunk_metadata = ChunkMetadata(
                chunk_index=i,
                source_name=filename,
                content=chunk,
                custom_metadata=custom_metadata
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=chunk_metadata.model_dump()
                )
            )

        logger.info(f"Document processing complete: {len(points)} points created")
        return points
