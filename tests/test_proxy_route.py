import asyncio
import time
from types import SimpleNamespace
from typing import Any

import pytest

from app import routes
from app.routes import proxy_to_primary
from app.schemas import ProxyRequest


class FakeSettings:
    primary_llm_url = "http://primary"
    candidate_llm_url = "http://candidate"


class SlowCandidateClient:
    def __init__(self, http_client: Any) -> None:
        self.http_client = http_client

    async def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        if url == "http://primary":
            return {
                "model": "primary",
                "output": {"answer": payload["prompt"]},
                "metadata": payload["metadata"],
            }

        await asyncio.sleep(0.25)
        return {"model": "candidate", "output": {"answer": "slow"}}


class FailingCandidateClient(SlowCandidateClient):
    async def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        if url == "http://primary":
            return {
                "model": "primary",
                "output": {"answer": payload["prompt"]},
                "metadata": payload["metadata"],
            }

        await asyncio.sleep(0.25)
        raise RuntimeError("candidate failed")


class MatchingCandidateClient(SlowCandidateClient):
    async def post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "model": "primary" if url == "http://primary" else "candidate",
            "output": {"answer": payload["prompt"]},
            "metadata": payload["metadata"],
        }


def fake_request() -> SimpleNamespace:
    state = SimpleNamespace(
        http_client=None,
        settings=FakeSettings(),
        shadow_tasks=set(),
    )
    return SimpleNamespace(app=SimpleNamespace(state=state))


@pytest.mark.asyncio
async def test_proxy_returns_primary_before_slow_candidate_finishes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes, "LLMClient", SlowCandidateClient)
    request = fake_request()
    payload = ProxyRequest(prompt="hello", metadata={"request_id": "fast"})

    started = time.perf_counter()
    response = await proxy_to_primary(payload, request)
    elapsed = time.perf_counter() - started

    assert response.model == "primary"
    assert response.output == {"answer": "hello"}
    assert elapsed < 0.1
    assert len(request.app.state.shadow_tasks) == 1

    await asyncio.gather(*request.app.state.shadow_tasks)


@pytest.mark.asyncio
async def test_proxy_shadow_task_does_not_log_when_candidate_matches_primary(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes, "LLMClient", MatchingCandidateClient)
    request = fake_request()
    payload = ProxyRequest(prompt="hello", metadata={"request_id": "match"})

    response = await proxy_to_primary(payload, request)
    await asyncio.gather(*request.app.state.shadow_tasks)

    assert response.model == "primary"
    assert response.output == {"answer": "hello"}
    assert "LLM output mismatch" not in caplog.text


@pytest.mark.asyncio
async def test_proxy_response_is_not_blocked_by_candidate_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes, "LLMClient", FailingCandidateClient)
    request = fake_request()
    payload = ProxyRequest(prompt="hello", metadata={"request_id": "failure"})

    started = time.perf_counter()
    response = await proxy_to_primary(payload, request)
    elapsed = time.perf_counter() - started

    assert response.model == "primary"
    assert response.output == {"answer": "hello"}
    assert elapsed < 0.1

    await asyncio.gather(*request.app.state.shadow_tasks)
