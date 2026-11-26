"""Command Executor: runs a Simulation Request (Ch. 5.2, ADR-002)."""

from rover.domain.model import (
    BlockedMove,
    Heading,
    Position,
    SimulationRequest,
    SimulationResult,
)
from rover.domain.navigator import Navigator


class CommandExecutor:
    def __init__(self) -> None:
        self._navigator = Navigator()

    def execute(self, request: SimulationRequest) -> SimulationResult:
        position = request.start
        heading = request.heading
        blocked: list[BlockedMove] = []
        for index, command in enumerate(request.commands):
            outcome = self._navigator.apply(command, position, heading, request.grid)
            if isinstance(outcome, Position):
                position = outcome
            elif isinstance(outcome, Heading):
                heading = outcome
            elif isinstance(outcome, BlockedMove):
                blocked.append(BlockedMove(index=index, reason=outcome.reason))
        return SimulationResult(position=position, heading=heading, blocked=blocked)
