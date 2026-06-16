from typing import Any

import pytest

from app.services.shadow import run_shadow_comparison


class FakeClient:
    async def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"model": "candidate", "output": {"answer": "different"}}


class MatchingClient:
    async def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"model": "candidate", "output": {"answer": "primary"}}


class FailingClient:
    async def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("candidate unavailable")


@pytest.mark.asyncio
async def test_shadow_logs_mismatch(caplog: pytest.LogCaptureFixture) -> None:
    await run_shadow_comparison(
        client=FakeClient(),
        candidate_url="http://candidate",
        request_payload={"metadata": {"request_id": "test"}},
        primary_payload={"model": "primary", "output": {"answer": "primary"}},
    )

    assert "LLM output mismatch" in caplog.text


@pytest.mark.asyncio
async def test_shadow_does_not_log_when_outputs_match(
    caplog: pytest.LogCaptureFixture,
) -> None:
    await run_shadow_comparison(
        client=MatchingClient(),
        candidate_url="http://candidate",
        request_payload={"metadata": {"request_id": "test"}},
        primary_payload={"model": "primary", "output": {"answer": "primary"}},
    )

    assert "LLM output mismatch" not in caplog.text


@pytest.mark.asyncio
async def test_shadow_candidate_failure_does_not_raise(
    caplog: pytest.LogCaptureFixture,
) -> None:
    await run_shadow_comparison(
        client=FailingClient(),
        candidate_url="http://candidate",
        request_payload={"metadata": {"request_id": "test"}},
        primary_payload={"model": "primary", "output": {"answer": "primary"}},
    )

    assert "Candidate shadow request failed" in caplog.text
