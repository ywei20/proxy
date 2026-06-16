import logging
from typing import Any

from app.services.llm_client import LLMClient
from app.services.metrics import ShadowMetrics
from app.utils.json_extract import extract_json_payload

logger = logging.getLogger("proxy.shadow")


async def run_shadow_comparison(
    *,
    client: LLMClient,
    candidate_url: str,
    request_payload: dict[str, Any],
    primary_payload: dict[str, Any],
    metrics: ShadowMetrics | None = None,
) -> None:
    try:
        candidate_payload = await client.post(candidate_url, request_payload)
    except Exception:
        if metrics is not None:
            metrics.record_candidate_failure()
        logger.exception("Candidate shadow request failed")
        return

    primary_output = extract_json_payload(primary_payload.get("output"))
    candidate_output = extract_json_payload(candidate_payload.get("output"))

    if primary_output == candidate_output:
        if metrics is not None:
            metrics.record_match()
    else:
        if metrics is not None:
            metrics.record_mismatch()
        logger.warning(
            "LLM output mismatch",
            extra={
                "request_metadata": request_payload.get("metadata", {}),
                "primary_payload": primary_output,
                "candidate_payload": candidate_output,
            },
        )
