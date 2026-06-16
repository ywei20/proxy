from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    primary_llm_url: str = "http://127.0.0.1:8000/simulated/primary"
    candidate_llm_url: str = "http://127.0.0.1:8000/simulated/candidate"
    llm_timeout_seconds: float = 10.0
