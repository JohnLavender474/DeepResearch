from typing import Literal, get_args


ModelType = Literal["claude", "openai", "dummy"]

MODEL_TYPES: list[str] = list(get_args(ModelType))
