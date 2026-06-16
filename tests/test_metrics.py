from types import SimpleNamespace

import pytest

from app.routes import metrics
from app.services.metrics import ShadowMetrics


def test_shadow_metrics_snapshot_starts_empty() -> None:
    shadow_metrics = ShadowMetrics()

    assert shadow_metrics.snapshot() == {
        "total_comparisons": 0,
        "matched_comparisons": 0,
        "mismatched_comparisons": 0,
        "failed_candidate_requests": 0,
        "match_rate_percent": 0.0,
    }


def test_shadow_metrics_match_rate_percent() -> None:
    shadow_metrics = ShadowMetrics()
    shadow_metrics.record_match()
    shadow_metrics.record_mismatch()

    assert shadow_metrics.snapshot()["match_rate_percent"] == 50.0


@pytest.mark.asyncio
async def test_metrics_route_returns_current_shadow_metrics() -> None:
    shadow_metrics = ShadowMetrics()
    shadow_metrics.record_match()
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(shadow_metrics=shadow_metrics))
    )

    assert await metrics(request) == {
        "total_comparisons": 1,
        "matched_comparisons": 1,
        "mismatched_comparisons": 0,
        "failed_candidate_requests": 0,
        "match_rate_percent": 100.0,
    }
