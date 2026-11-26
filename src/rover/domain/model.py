"""Domain types of the Mars Rover Simulator (Ch. 5.2, ADR-004)."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class Heading(Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"


class Command(Enum):
    F = "F"
    L = "L"
    R = "R"


@dataclass(frozen=True)
class Position:
    x: int
    y: int


@dataclass(frozen=True)
class Grid:
    width: int
    height: int
    obstacles: frozenset[Position] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SimulationRequest:
    start: Position
    heading: Heading
    grid: Grid
    commands: list[Command]


@dataclass(frozen=True)
class BlockedMove:
    index: int
    reason: Literal["obstacle", "boundary"]


@dataclass(frozen=True)
class SimulationResult:
    position: Position
    heading: Heading
    blocked: list[BlockedMove] = field(default_factory=list)
