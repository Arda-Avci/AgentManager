from __future__ import annotations

from src.recovery.manager import RecoveryManager
from src.api.routes import _get_recovery


class TestRecoveryManager:
    def test_register_agent(self):
        mgr = RecoveryManager()
        mgr.register_agent("agent-1")
        status = mgr.get_status("agent-1")
        assert status["status"] == "healthy"
        assert status["restart_count"] == 0

    def test_on_crash_restarts(self):
        mgr = RecoveryManager(max_restarts=3)
        mgr.register_agent("agent-1")
        result = mgr.on_crash("agent-1", ValueError("connection lost"))
        assert result["restarted"] is True
        assert result["status"] == "recovering"

    def test_max_restarts_exceeded(self):
        mgr = RecoveryManager(max_restarts=2)
        mgr.register_agent("agent-1")
        mgr.on_crash("agent-1", "err1")
        mgr.on_crash("agent-1", "err2")
        result = mgr.on_crash("agent-1", "err3")
        assert result["restarted"] is False
        assert result["status"] == "dead"

    def test_get_status_with_uptime(self):
        mgr = RecoveryManager()
        mgr.register_agent("agent-1")
        status = mgr.get_status("agent-1")
        assert "uptime_seconds" in status
        assert status["uptime_seconds"] is not None

    def test_get_status_unregistered(self):
        mgr = RecoveryManager()
        status = mgr.get_status("unknown-agent")
        assert status["status"] == "unknown"

    def test_crash_tracks_error(self):
        mgr = RecoveryManager()
        mgr.register_agent("agent-1")
        mgr.on_crash("agent-1", RuntimeError("timeout"))
        status = mgr.get_status("agent-1")
        assert "timeout" in status["last_error"]
