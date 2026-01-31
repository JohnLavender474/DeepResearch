import os

from dotenv import load_dotenv


load_dotenv()


def _get_required_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value


QDRANT_URL = _get_required_env_var("QDRANT_URL")

SENTENCE_TRANSFORMER_MODEL = _get_required_env_var("SENTENCE_TRANSFORMER_MODEL")