"""FastAPI Route Adapter: JSON request/response mapping (Ch. 5.2, ADR-007)."""

import time
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

from rover.adapters.logger import LoggerAdapter
from rover.domain.executor import CommandExecutor
from rover.domain.model import Command, Grid, Heading, Position, SimulationRequest

router = APIRouter()
_executor = CommandExecutor()
_logger = LoggerAdapter()


class PositionPayload(BaseModel):
    x: int
    y: int


class StartPayload(PositionPayload):
    heading: str


class GridPayload(BaseModel):
    width: int
    height: int
    obstacles: list[PositionPayload] = Field(default_factory=list)


class SimulationRequestPayload(BaseModel):
    start: StartPayload
    grid: GridPayload
    commands: str


class BlockedMovePayload(BaseModel):
    index: int
    reason: str


class SimulationResultPayload(BaseModel):
    position: PositionPayload
    heading: str
    blocked: list[BlockedMovePayload]


@router.post("/simulate", response_model=SimulationResultPayload)
def simulate(payload: SimulationRequestPayload) -> SimulationResultPayload:
    started_at = time.perf_counter()
    request_id = str(uuid4())
    request = SimulationRequest(
        start=Position(x=payload.start.x, y=payload.start.y),
        heading=Heading(payload.start.heading),
        grid=Grid(
            width=payload.grid.width,
            height=payload.grid.height,
            obstacles=frozenset(
                Position(x=obstacle.x, y=obstacle.y)
                for obstacle in payload.grid.obstacles
            ),
        ),
        commands=[Command(character) for character in payload.commands],
    )
    result = _executor.execute(request)
    _logger.log_simulation_complete(
        request_id=request_id,
        grid=request.grid,
        start=request.start,
        heading=request.heading,
        command_count=len(request.commands),
        result=result,
        duration_ms=(time.perf_counter() - started_at) * 1000,
    )
    return SimulationResultPayload(
        position=PositionPayload(x=result.position.x, y=result.position.y),
        heading=result.heading.value,
        blocked=[
            BlockedMovePayload(index=move.index, reason=move.reason)
            for move in result.blocked
        ],
    )
