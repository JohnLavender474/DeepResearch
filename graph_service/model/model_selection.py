from typing import Literal, get_args


ModelType = Literal["claude", "ollama"]

MODEL_TYPES: list[str] = list(get_args(ModelType))
