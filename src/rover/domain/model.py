"""Domain types of the Mars Rover Simulator (Ch. 5.2, ADR-004)."""

from dataclasses import dataclass, field
from enum import Enum


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
