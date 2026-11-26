"""Navigator: applies a single command to the rover (Ch. 5.2, ADR-002)."""

from rover.domain.model import BlockedMove, Command, Grid, Heading, Position

# Navigator has no Command List index; the Executor assigns it (Ch. 5.2).
_UNINDEXED = 0

# Turn Left rotates the heading 90° anticlockwise (Ch. 12 Glossary)
_LEFT_OF = {
    Heading.N: Heading.W,
    Heading.W: Heading.S,
    Heading.S: Heading.E,
    Heading.E: Heading.N,
}

# Turn Right rotates the heading 90° clockwise (Ch. 12 Glossary)
_RIGHT_OF = {
    Heading.N: Heading.E,
    Heading.E: Heading.S,
    Heading.S: Heading.W,
    Heading.W: Heading.N,
}

_TURNS = {
    Command.L: _LEFT_OF,
    Command.R: _RIGHT_OF,
}

# North increases y, east increases x (Ch. 12 Glossary)
_FORWARD_STEPS = {
    Heading.N: (0, 1),
    Heading.E: (1, 0),
    Heading.S: (0, -1),
    Heading.W: (-1, 0),
}


class Navigator:
    def apply(
        self, command: Command, position: Position, heading: Heading, grid: Grid
    ) -> Position | Heading | BlockedMove:
        if command is Command.F:
            dx, dy = _FORWARD_STEPS[heading]
            target = Position(x=position.x + dx, y=position.y + dy)
            if target in grid.obstacles:
                return BlockedMove(index=_UNINDEXED, reason="obstacle")
            return target
        return _TURNS[command][heading]
