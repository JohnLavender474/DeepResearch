import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")