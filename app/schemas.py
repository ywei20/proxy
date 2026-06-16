from typing import Any

from pydantic import BaseModel, Field


class ProxyRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    candidate_override: Any | None = None


class LLMResponse(BaseModel):
    model: str
    output: Any
    metadata: dict[str, Any] = Field(default_factory=dict)
