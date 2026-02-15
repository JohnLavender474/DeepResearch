from typing import Any

from pathlib import Path


def load_prompt(
    filename: str,
    args: dict[str, Any] | None = None,
) -> str:
    prompt_dir = Path(__file__).parent.parent / "prompts"
    prompt_path = prompt_dir / filename

    with open(prompt_path, "r") as f:
        prompt = f.read()

    if args:
        prompt = prompt.format(**args)

    return prompt
