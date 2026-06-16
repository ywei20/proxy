import asyncio
from copy import deepcopy

from fastapi import APIRouter, Request

from app.schemas import LLMResponse, ProxyRequest
from app.services.llm_client import LLMClient
from app.services.metrics import ShadowMetrics
from app.services.shadow import run_shadow_comparison

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/hello")
async def hello() -> dict[str, str]:
    return {"message": "hello world"}


@router.get("/metrics")
async def metrics(request: Request) -> dict[str, int | float]:
    shadow_metrics: ShadowMetrics = request.app.state.shadow_metrics
    return shadow_metrics.snapshot()


@router.post("/v1/proxy", response_model=LLMResponse)
async def proxy_to_primary(payload: ProxyRequest, request: Request) -> LLMResponse:
    client = LLMClient(request.app.state.http_client)
    settings = request.app.state.settings

    primary_response = await client.post(settings.primary_llm_url, payload.model_dump())

    shadow_task = asyncio.create_task(
        run_shadow_comparison(
            client=client,
            candidate_url=settings.candidate_llm_url,
            request_payload=deepcopy(payload.model_dump()),
            primary_payload=deepcopy(primary_response),
            metrics=request.app.state.shadow_metrics,
        )
    )
    request.app.state.shadow_tasks.add(shadow_task)
    shadow_task.add_done_callback(request.app.state.shadow_tasks.discard)

    return LLMResponse.model_validate(primary_response)


@router.post("/simulated/primary", response_model=LLMResponse)
async def simulated_primary(payload: ProxyRequest) -> LLMResponse:
    return LLMResponse(
        model="primary",
        output={"answer": payload.prompt, "source": "primary"},
        metadata=payload.metadata,
    )


@router.post("/simulated/candidate", response_model=LLMResponse)
async def simulated_candidate(payload: ProxyRequest) -> LLMResponse:
    output = payload.candidate_override
    if output is None:
        output = {"answer": payload.prompt, "source": "candidate"}

    return LLMResponse(
        model="candidate",
        output=output,
        metadata=payload.metadata,
    )
