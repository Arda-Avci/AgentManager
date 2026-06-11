from __future__ import annotations

import pytest

from src.logging.detector import LoopDetector
from src.logging.manager import LogManager
from src.logging.models import ActionLog


@pytest.mark.asyncio
async def test_no_loop_with_few_actions():
    log = LogManager()
    detector = LoopDetector(log)
    for i in range(2):
        a = ActionLog(agent_id="a1", task_id="t1", action_name="research", params={"q": str(i)})
        await log.log_action("a1", "t1", a)
    assert detector.detect_loop("a1", "t1") is False


@pytest.mark.asyncio
async def test_detect_loop_on_repeated_actions():
    log = LogManager()
    detector = LoopDetector(log)
    for i in range(5):
        a = ActionLog(agent_id="a1", task_id="t1", action_name="research", params={"q": "same"})
        await log.log_action("a1", "t1", a)
    assert detector.detect_loop("a1", "t1") is True


@pytest.mark.asyncio
async def test_no_loop_with_different_actions():
    log = LogManager()
    detector = LoopDetector(log)
    for i in range(5):
        a = ActionLog(agent_id="a1", task_id="t1", action_name="research", params={"q": f"query_{i}"})
        await log.log_action("a1", "t1", a)
    assert detector.detect_loop("a1", "t1") is False


@pytest.mark.asyncio
async def test_suggest_fix_returns_none_when_no_loop():
    log = LogManager()
    detector = LoopDetector(log)
    a = ActionLog(agent_id="a1", task_id="t1", action_name="research", params={"q": "hello"})
    await log.log_action("a1", "t1", a)
    suggestion = detector.suggest_fix("a1", "t1")
    assert suggestion is None


@pytest.mark.asyncio
async def test_suggest_fix_returns_hint_on_loop():
    log = LogManager()
    detector = LoopDetector(log)
    for i in range(4):
        a = ActionLog(agent_id="a1", task_id="t1", action_name="research", params={"q": "same"})
        await log.log_action("a1", "t1", a)
    suggestion = detector.suggest_fix("a1", "t1")
    assert suggestion is not None
    assert "Loop detected" in suggestion
    assert "research" in suggestion
