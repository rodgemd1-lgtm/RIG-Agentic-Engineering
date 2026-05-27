"""Deterministic state machine for RIG RunEnvelope lifecycle.

Core law:
    No RunEnvelope, no run.
    No state machine, no long-horizon autonomy.

Valid transitions:
    draft → building
    building → needs_approval
    building → failed
    needs_approval → completed (with approval)
    needs_approval → failed

Forbidden transitions:
    failed → completed          # Must restart
    needs_approval → completed  # Without approval
    building → completed        # Without verify
    completed → *              # Terminal
    failed → *                  # Terminal (unless explicit restart)
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional


class RunState(str, enum.Enum):
    """Finite states for a RIG build mission."""
    DRAFT = "draft"
    BUILDING = "building"
    NEEDS_APPROVAL = "needs_approval"
    COMPLETED = "completed"
    FAILED = "failed"


# Transition graph: current_state → {allowed_next_states}
VALID_TRANSITIONS: dict[RunState, set[RunState]] = {
    RunState.DRAFT: {RunState.BUILDING},
    RunState.BUILDING: {RunState.NEEDS_APPROVAL, RunState.FAILED},
    RunState.NEEDS_APPROVAL: {RunState.COMPLETED, RunState.FAILED},
    RunState.COMPLETED: set(),  # Terminal
    RunState.FAILED: set(),       # Terminal
}


@dataclass
class TransitionResult:
    """Result of attempting a state transition."""
    success: bool
    from_state: RunState
    to_state: RunState
    error: Optional[str] = None
    requires_approval: bool = False


class StateMachine:
    """Deterministic state machine for RunEnvelope lifecycle.
    
    Every transition is validated against VALID_TRANSITIONS.
    Invalid transitions raise RuntimeError.
    """
    
    def __init__(self, initial_state: RunState = RunState.DRAFT) -> None:
        self._state = initial_state
        self._history: list[tuple[str, str]] = []  # (from, to) for audit trail
    
    @property
    def state(self) -> RunState:
        return self._state
    
    @property
    def history(self) -> list[tuple[str, str]]:
        """Immutable audit trail of all transitions."""
        return self._history.copy()
    
    def can_transition(self, new_state: RunState) -> TransitionResult:
        """Check if a transition is allowed without changing state."""
        if new_state == self._state:
            return TransitionResult(
                success=True,
                from_state=self._state,
                to_state=new_state,
            )
        
        allowed = VALID_TRANSITIONS.get(self._state, set())
        if new_state not in allowed:
            return TransitionResult(
                success=False,
                from_state=self._state,
                to_state=new_state,
                error=f"Forbidden transition: {self._state.value} → {new_state.value}. "
                      f"Allowed: {[s.value for s in allowed]}",
            )
        
        # Special case: needs_approval → completed requires approval flag
        if self._state == RunState.NEEDS_APPROVAL and new_state == RunState.COMPLETED:
            return TransitionResult(
                success=True,  # Structurally allowed, but caller must verify approval
                from_state=self._state,
                to_state=new_state,
                requires_approval=True,
            )
        
        return TransitionResult(
            success=True,
            from_state=self._state,
            to_state=new_state,
        )
    
    def transition(self, new_state: RunState, *, approval_granted: bool = False) -> TransitionResult:
        """Attempt a state transition.
        
        Args:
            new_state: Target state
            approval_granted: Must be True for needs_approval → completed
            
        Raises:
            RuntimeError: If transition is forbidden
            ValueError: If approval required but not granted
        """
        result = self.can_transition(new_state)
        
        if not result.success:
            raise RuntimeError(result.error)
        
        if result.requires_approval and not approval_granted:
            raise ValueError(
                f"Transition {self._state.value} → {new_state.value} requires approval. "
                "Set approval_granted=True or route to approver."
            )
        
        self._history.append((self._state.value, new_state.value))
        self._state = new_state
        return TransitionResult(
            success=True,
            from_state=RunState(self._history[-1][0]),
            to_state=new_state,
        )
    
    def is_terminal(self) -> bool:
        """Check if current state is terminal (no further transitions)."""
        return len(VALID_TRANSITIONS.get(self._state, set())) == 0
    
    def must_approve(self) -> bool:
        """Check if current state requires approval before next step."""
        return self._state == RunState.NEEDS_APPROVAL
