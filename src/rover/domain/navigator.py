"""Navigator: applies a single command to the rover (Ch. 5.2, ADR-002)."""

from rover.domain.model import Command, Grid, Heading, Position

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


class Navigator:
    def apply(
        self, command: Command, position: Position, heading: Heading, grid: Grid
    ) -> tuple[Position, Heading]:
        return position, _TURNS[command][heading]
