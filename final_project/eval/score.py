"""Score a Juice Shop instance by querying its /api/Challenges endpoint.

This is the ground truth for grading. Do not modify.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class ChallengeResult:
    key: str
    name: str
    category: str
    difficulty: int
    solved: bool
    description: str

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "ChallengeResult":
        return cls(
            key=raw.get("key") or raw.get("name", ""),
            name=raw.get("name", ""),
            category=raw.get("category", ""),
            difficulty=int(raw.get("difficulty", 0)),
            solved=bool(raw.get("solved", False)),
            description=raw.get("description", ""),
        )


@dataclass
class Scorecard:
    target: str
    total: int
    solved: int
    challenges: list[ChallengeResult]

    @property
    def fraction(self) -> float:
        return (self.solved / self.total) if self.total else 0.0

    def by_category(self) -> dict[str, tuple[int, int]]:
        out: dict[str, list[int]] = {}
        for c in self.challenges:
            s, t = out.setdefault(c.category, [0, 0])
            out[c.category] = [s + int(c.solved), t + 1]
        return {k: (v[0], v[1]) for k, v in out.items()}

    def solved_challenges(self) -> list[ChallengeResult]:
        return [c for c in self.challenges if c.solved]


def score_target(target_url: str, timeout: float = 10.0) -> Scorecard:
    url = target_url.rstrip("/") + "/api/Challenges/"
    response = httpx.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    raw_challenges = payload.get("data", payload)
    challenges = [ChallengeResult.from_api(c) for c in raw_challenges]
    solved = sum(1 for c in challenges if c.solved)
    return Scorecard(
        target=target_url,
        total=len(challenges),
        solved=solved,
        challenges=challenges,
    )
