import os

from dotenv import load_dotenv


load_dotenv()


def _get_optional_env_var(var_name, default_value):
    return os.getenv(var_name, default_value)


BLOB_STORAGE_PATH = _get_optional_env_var(
    var_name="BLOB_STORAGE_PATH",
    default_value="./blob_storage"
)

DATABASE_SERVICE_URL = _get_optional_env_var(
    var_name="DATABASE_SERVICE_URL",
    default_value="http://localhost:8003/api/database"
)

EMBEDDING_SERVICE_URL = _get_optional_env_var(
    var_name="EMBEDDING_SERVICE_URL",
    default_value="http://localhost:8000/api/embeddings"
)
