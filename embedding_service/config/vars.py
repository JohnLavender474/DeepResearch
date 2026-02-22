import os

from dotenv import load_dotenv


load_dotenv()


def _get_required_env_var(var_name):
    value = os.getenv(var_name)
    if value is None or not value.strip():
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value


QDRANT_URL = _get_required_env_var("QDRANT_URL")

SENTENCE_TRANSFORMER_MODEL = os.getenv(
    "SENTENCE_TRANSFORMER_MODEL",
    "all-MiniLM-L6-v2"
).strip() or "all-MiniLM-L6-v2"


def _get_optional_env_var(var_name, default_value):
    return os.getenv(var_name, default_value)


DATABASE_SERVICE_URL = _get_optional_env_var(
    var_name="DATABASE_SERVICE_URL",
    default_value="http://localhost:8003/api/database"
)

MAX_UPLOAD_SIZE_MB = int(
    _get_optional_env_var(
        var_name="MAX_UPLOAD_SIZE_MB",
        default_value="50"
    )
)
