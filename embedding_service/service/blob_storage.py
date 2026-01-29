import os
import logging
import shutil
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class BlobStorage:

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"BlobStorage initialized with path: {self.storage_path}"
        )


    def store_blob(
        self,
        collection_name: str,
        filename: str,
        file_path: str
    ) -> str:
        collection_dir = self.storage_path / collection_name
        collection_dir.mkdir(parents=True, exist_ok=True)

        dest_path = collection_dir / filename
        shutil.copy2(file_path, dest_path)

        logger.info(
            f"Stored blob: collection='{collection_name}', "
            f"filename='{filename}', path='{dest_path}'"
        )
        return str(dest_path)


    def retrieve_blob(
        self,
        collection_name: str,
        filename: str
    ) -> Optional[bytes]:
        blob_path = self.storage_path / collection_name / filename

        if not blob_path.exists():
            logger.warning(
                f"Blob not found: collection='{collection_name}', "
                f"filename='{filename}'"
            )
            return None

        with open(blob_path, "rb") as f:
            content = f.read()

        logger.info(
            f"Retrieved blob: collection='{collection_name}', "
            f"filename='{filename}', path='{blob_path}'"
        )
        return content


    def delete_blob(
        self,
        collection_name: str,
        filename: str
    ) -> bool:
        blob_path = self.storage_path / collection_name / filename

        if not blob_path.exists():
            logger.warning(
                f"Blob not found for deletion: collection='{collection_name}', "
                f"filename='{filename}'"
            )
            return False

        os.remove(blob_path)
        logger.info(
            f"Deleted blob: collection='{collection_name}', "
            f"filename='{filename}'"
        )
        return True


    def list_blobs(self, collection_name: str) -> list[str]:
        collection_dir = self.storage_path / collection_name

        if not collection_dir.exists():
            logger.debug(f"Collection directory not found: {collection_name}")
            return []

        filenames = [
            f.name for f in collection_dir.iterdir() if f.is_file()
        ]
        logger.debug(
            f"Listed {len(filenames)} blobs in collection '{collection_name}'"
        )
        return filenames


    def delete_collection(self, collection_name: str) -> bool:
        collection_dir = self.storage_path / collection_name

        if not collection_dir.exists():
            logger.warning(f"Collection not found: {collection_name}")
            return False

        shutil.rmtree(collection_dir)
        logger.info(f"Deleted collection directory: {collection_name}")
        return True
