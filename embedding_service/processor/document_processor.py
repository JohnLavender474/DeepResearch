import uuid
import logging

from typing import Any, Generator

from pypdf import PdfReader
from qdrant_client.models import PointStruct

from service.embedding_service import EmbeddingService
from model.chunk_metadata import ChunkMetadata
from model.document_chunk import DocumentChunk


logger = logging.getLogger(__name__)


class DocumentProcessor:

    def __init__(self, embedding_service: EmbeddingService):
        logger.info("Initializing DocumentProcessor")
        self.embedding_service = embedding_service


    def _chunk_file(
        self,
        file_path: str,
        chunk_size: int
    ) -> Generator[DocumentChunk, None, None]:
        logger.debug(f"Extracting and chunking file: {file_path}")
        
        if file_path.endswith('.pdf'):
            logger.debug(f"Extracting text from PDF: {file_path}")
            reader = PdfReader(file_path)
            
            current_chunk_words = []
            current_size = 0
            current_page = -1
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                words = text.split()
                
                for word in words:
                    word_size = len(word) + 1
                    
                    if (
                        current_size + word_size > chunk_size and
                        len(current_chunk_words) != 0
                    ):
                        yield DocumentChunk(
                            page_number=current_page,
                            text=" ".join(current_chunk_words)
                        )
                        current_chunk_words = [word]
                        current_size = word_size
                        current_page = page_num
                    else:
                        if current_page is None:
                            current_page = page_num
                        current_chunk_words.append(word)
                        current_size += word_size
            
            if current_chunk_words:
                yield DocumentChunk(
                    page_number=current_page,
                    text=" ".join(current_chunk_words)
                )
        
        elif file_path.endswith('.txt'):
            logger.debug(f"Extracting text from file: {file_path}")
            current_chunk_words = []
            current_size = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    words = line.split()
                    
                    for word in words:
                        word_size = len(word) + 1
                        
                        if (
                            current_size + word_size > chunk_size and
                            len(current_chunk_words) != 0
                        ):
                            yield DocumentChunk(
                                page_number=1,
                                text=" ".join(current_chunk_words)
                            )
                            current_chunk_words = [word]
                            current_size = word_size
                        else:
                            current_chunk_words.append(word)
                            current_size += word_size
                
                if current_chunk_words:
                    yield DocumentChunk(
                        page_number=1,
                        text=" ".join(current_chunk_words)
                    )

        else:
            logger.error(f"Unsupported file format for {file_path}")
            raise ValueError(
                f"Unsupported file format. Supported: .pdf, .txt"
            )


    def process_document(
        self,
        file_path: str,
        filename: str,
        chunk_size: int = 2000,
        custom_metadata: dict[str, Any] = {}
    ) -> Generator[PointStruct, None, None]:
        logger.info(f"Processing document: {filename}")
        
        chunk_index = 0
        for chunk in self._chunk_file(
            file_path=file_path,
            chunk_size=chunk_size
        ):
            vector = self.embedding_service.get_encoding(chunk.text)

            point_id = str(uuid.uuid4())

            chunk_metadata = ChunkMetadata(
                chunk_index=chunk_index,
                source_name=filename,
                content=chunk.text,
                page_number=chunk.page_number,
                custom_metadata=custom_metadata
            )

            yield PointStruct(
                id=point_id,
                vector=vector,
                payload=chunk_metadata.model_dump()
            )

            chunk_index += 1

        logger.info(
            f"Document processing complete: {filename}"
        )
