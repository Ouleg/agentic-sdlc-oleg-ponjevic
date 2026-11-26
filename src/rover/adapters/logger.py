"""Logger Adapter: one structured JSON entry per request (Ch. 5.2, ADR-005)."""

import json
import logging
import sys

from rover.domain.model import Grid, Heading, Position, SimulationResult


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(record.msg)


class LoggerAdapter:
    def __init__(self) -> None:
        self._logger = logging.getLogger("rover")
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        self._logger.handlers = [handler]
        self._logger.propagate = False

    def log_simulation_complete(
        self,
        request_id: str,
        grid: Grid,
        start: Position,
        heading: Heading,
        command_count: int,
        result: SimulationResult,
        duration_ms: float,
    ) -> None:
        self._logger.info(
            {
                "level": "INFO",
                "event": "simulation_complete",
                "request_id": request_id,
                "grid": {
                    "width": grid.width,
                    "height": grid.height,
                    "obstacle_count": len(grid.obstacles),
                },
                "start": {"x": start.x, "y": start.y, "heading": heading.value},
                "command_count": command_count,
                "result": {
                    "x": result.position.x,
                    "y": result.position.y,
                    "heading": result.heading.value,
                    "blocked_count": len(result.blocked),
                },
                "error": None,
                "duration_ms": duration_ms,
            }
        )
