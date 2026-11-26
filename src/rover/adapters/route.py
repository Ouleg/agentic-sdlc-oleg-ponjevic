"""FastAPI Route Adapter: JSON request/response mapping (Ch. 5.2, ADR-007)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from rover.domain.executor import CommandExecutor
from rover.domain.model import Command, Grid, Heading, Position, SimulationRequest

router = APIRouter()
_executor = CommandExecutor()


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
    return SimulationResultPayload(
        position=PositionPayload(x=result.position.x, y=result.position.y),
        heading=result.heading.value,
        blocked=[
            BlockedMovePayload(index=move.index, reason=move.reason)
            for move in result.blocked
        ],
    )
