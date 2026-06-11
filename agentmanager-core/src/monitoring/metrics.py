from __future__ import annotations

import time
from collections import defaultdict
from typing import Any


class MetricsCollector:
    def __init__(self):
        self._request_durations: dict[str, list[float]] = defaultdict(list)
        self._token_usage: dict[str, list[int]] = defaultdict(list)
        self._request_counts: dict[str, int] = defaultdict(int)

    def track_request_duration(self, endpoint: str, duration_ms: float) -> None:
        self._request_durations[endpoint].append(duration_ms)
        self._request_counts[endpoint] += 1

    def track_token_usage(self, agent_id: str, count: int) -> None:
        self._token_usage[agent_id].append(count)

    def get_metrics(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "endpoints": {},
            "token_usage": {},
            "total_requests": 0,
        }
        for endpoint, durations in self._request_durations.items():
            avg = sum(durations) / len(durations) if durations else 0.0
            result["endpoints"][endpoint] = {
                "count": self._request_counts[endpoint],
                "avg_duration_ms": round(avg, 2),
                "max_duration_ms": round(max(durations), 2) if durations else 0.0,
                "min_duration_ms": round(min(durations), 2) if durations else 0.0,
            }
            result["total_requests"] += self._request_counts[endpoint]

        for agent_id, counts in self._token_usage.items():
            result["token_usage"][agent_id] = {
                "total": sum(counts),
                "count": len(counts),
                "avg": round(sum(counts) / len(counts), 2) if counts else 0,
            }
        return result

    def reset(self) -> None:
        self._request_durations.clear()
        self._token_usage.clear()
        self._request_counts.clear()


_collector = MetricsCollector()


def get_collector() -> MetricsCollector:
    return _collector
