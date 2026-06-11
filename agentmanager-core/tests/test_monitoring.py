from __future__ import annotations

import pytest

from src.monitoring.metrics import MetricsCollector


class TestMetricsCollector:
    def setup_method(self):
        self.collector = MetricsCollector()

    def test_track_request_duration(self):
        self.collector.track_request_duration("/api/v1/agents", 150.5)
        self.collector.track_request_duration("/api/v1/agents", 200.3)
        metrics = self.collector.get_metrics()
        assert metrics["total_requests"] == 2
        assert metrics["endpoints"]["/api/v1/agents"]["count"] == 2
        assert metrics["endpoints"]["/api/v1/agents"]["avg_duration_ms"] == pytest.approx(175.4, rel=1e-2)

    def test_track_token_usage(self):
        self.collector.track_token_usage("agent-1", 150)
        self.collector.track_token_usage("agent-1", 250)
        metrics = self.collector.get_metrics()
        assert metrics["token_usage"]["agent-1"]["total"] == 400
        assert metrics["token_usage"]["agent-1"]["count"] == 2

    def test_multiple_endpoints(self):
        self.collector.track_request_duration("/api/v1/agents", 100.0)
        self.collector.track_request_duration("/api/v1/chat", 200.0)
        metrics = self.collector.get_metrics()
        assert len(metrics["endpoints"]) == 2

    def test_reset(self):
        self.collector.track_request_duration("/api/v1/agents", 100.0)
        self.collector.reset()
        metrics = self.collector.get_metrics()
        assert metrics["total_requests"] == 0
