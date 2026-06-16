from dataclasses import dataclass


@dataclass
class ShadowMetrics:
    total_comparisons: int = 0
    matched_comparisons: int = 0
    mismatched_comparisons: int = 0
    failed_candidate_requests: int = 0

    def record_match(self) -> None:
        self.total_comparisons += 1
        self.matched_comparisons += 1

    def record_mismatch(self) -> None:
        self.total_comparisons += 1
        self.mismatched_comparisons += 1

    def record_candidate_failure(self) -> None:
        self.failed_candidate_requests += 1

    @property
    def match_rate_percent(self) -> float:
        if self.total_comparisons == 0:
            return 0.0
        return round((self.matched_comparisons / self.total_comparisons) * 100, 2)

    def snapshot(self) -> dict[str, int | float]:
        return {
            "total_comparisons": self.total_comparisons,
            "matched_comparisons": self.matched_comparisons,
            "mismatched_comparisons": self.mismatched_comparisons,
            "failed_candidate_requests": self.failed_candidate_requests,
            "match_rate_percent": self.match_rate_percent,
        }
