"""Tests for RIG Runtime Kernel State Machine.

Verifies deterministic state transitions and forbidden paths.
"""

from __future__ import annotations

import pytest

from runtime.kernel.state_machine import RunState, StateMachine, VALID_TRANSITIONS


class TestValidTransitions:
    def test_draft_to_building(self) -> None:
        sm = StateMachine(RunState.DRAFT)
        result = sm.transition(RunState.BUILDING)
        assert result.success is True
        assert sm.state == RunState.BUILDING

    def test_building_to_needs_approval(self) -> None:
        sm = StateMachine(RunState.BUILDING)
        result = sm.transition(RunState.NEEDS_APPROVAL)
        assert result.success is True
        assert sm.state == RunState.NEEDS_APPROVAL

    def test_building_to_failed(self) -> None:
        sm = StateMachine(RunState.BUILDING)
        result = sm.transition(RunState.FAILED)
        assert result.success is True
        assert sm.state == RunState.FAILED

    def test_needs_approval_to_failed(self) -> None:
        sm = StateMachine(RunState.NEEDS_APPROVAL)
        result = sm.transition(RunState.FAILED)
        assert result.success is True
        assert sm.state == RunState.FAILED

    def test_needs_approval_to_completed_with_approval(self) -> None:
        sm = StateMachine(RunState.NEEDS_APPROVAL)
        result = sm.transition(RunState.COMPLETED, approval_granted=True)
        assert result.success is True
        assert sm.state == RunState.COMPLETED


class TestForbiddenTransitions:
    def test_failed_to_completed_raises(self) -> None:
        sm = StateMachine(RunState.FAILED)
        with pytest.raises(RuntimeError, match="Forbidden transition"):
            sm.transition(RunState.COMPLETED)

    def test_needs_approval_to_completed_without_approval_raises(self) -> None:
        sm = StateMachine(RunState.NEEDS_APPROVAL)
        with pytest.raises(ValueError, match="requires approval"):
            sm.transition(RunState.COMPLETED)

    def test_building_to_completed_raises(self) -> None:
        sm = StateMachine(RunState.BUILDING)
        with pytest.raises(RuntimeError, match="Forbidden transition"):
            sm.transition(RunState.COMPLETED)

    def test_completed_to_anything_raises(self) -> None:
        sm = StateMachine(RunState.COMPLETED)
        with pytest.raises(RuntimeError, match="Forbidden transition"):
            sm.transition(RunState.FAILED)

    def test_failed_to_building_raises(self) -> None:
        sm = StateMachine(RunState.FAILED)
        with pytest.raises(RuntimeError, match="Forbidden transition"):
            sm.transition(RunState.BUILDING)


class TestTransitionHistory:
    def test_history_tracks_transitions(self) -> None:
        sm = StateMachine(RunState.DRAFT)
        sm.transition(RunState.BUILDING)
        sm.transition(RunState.NEEDS_APPROVAL)
        sm.transition(RunState.COMPLETED, approval_granted=True)
        
        assert len(sm.history) == 3
        assert sm.history[0] == ("draft", "building")
        assert sm.history[1] == ("building", "needs_approval")
        assert sm.history[2] == ("needs_approval", "completed")


class TestTerminalStates:
    def test_completed_is_terminal(self) -> None:
        sm = StateMachine(RunState.COMPLETED)
        assert sm.is_terminal() is True

    def test_failed_is_terminal(self) -> None:
        sm = StateMachine(RunState.FAILED)
        assert sm.is_terminal() is True

    def test_draft_is_not_terminal(self) -> None:
        sm = StateMachine(RunState.DRAFT)
        assert sm.is_terminal() is False

    def test_needs_approval_is_not_terminal(self) -> None:
        sm = StateMachine(RunState.NEEDS_APPROVAL)
        assert sm.is_terminal() is False


class TestApprovalCheck:
    def test_must_approve_in_needs_approval(self) -> None:
        sm = StateMachine(RunState.NEEDS_APPROVAL)
        assert sm.must_approve() is True

    def test_must_approve_in_building(self) -> None:
        sm = StateMachine(RunState.BUILDING)
        assert sm.must_approve() is False
