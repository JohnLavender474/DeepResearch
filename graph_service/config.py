import os

from dotenv import load_dotenv


load_dotenv()


def _get_required_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value


def _get_optional_env_var(var_name, default_value):
    return os.getenv(var_name, default_value)


CLAUDE_API_KEY = _get_optional_env_var(
    var_name="CLAUDE_API_KEY",
    default_value=None,
)

OPENAI_API_KEY = _get_optional_env_var(
    var_name="OPENAI_API_KEY",
    default_value=None,
)

OPENAI_MODEL = _get_optional_env_var(
    var_name="OPENAI_MODEL",
    default_value=None,
)

DEFAULT_LLM_MODEL = _get_optional_env_var(
    var_name="DEFAULT_LLM_MODEL",
    default_value="openai",
)

DATABASE_SERVICE_URL = _get_optional_env_var(
    var_name="DATABASE_SERVICE_URL",
    default_value="http://localhost:8003/api/database",
)

EMBEDDING_SERVICE_URL = _get_optional_env_var(
    var_name="EMBEDDING_SERVICE_URL",
    default_value="http://localhost:8000/api/embeddings",
)