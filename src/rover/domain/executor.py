"""Command Executor: runs a Simulation Request (Ch. 5.2, ADR-002)."""

from rover.domain.model import SimulationRequest, SimulationResult
from rover.domain.navigator import Navigator


class CommandExecutor:
    def __init__(self) -> None:
        self._navigator = Navigator()

    def execute(self, request: SimulationRequest) -> SimulationResult:
        position = request.start
        heading = request.heading
        for command in request.commands:
            position, heading = self._navigator.apply(
                command, position, heading, request.grid
            )
        return SimulationResult(position=position, heading=heading)
