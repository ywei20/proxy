import json
from typing import Any


def extract_json_payload(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return value

    stripped = _strip_markdown_fence(value.strip())
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(stripped):
        if char not in "{[":
            continue
        try:
            parsed, _ = decoder.raw_decode(stripped[index:])
            return parsed
        except json.JSONDecodeError:
            continue

    return value


def _strip_markdown_fence(value: str) -> str:
    if not value.startswith("```"):
        return value

    lines = value.splitlines()
    if len(lines) >= 2 and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return value
