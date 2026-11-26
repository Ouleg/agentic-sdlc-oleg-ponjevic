"""Navigator: applies a single command to the rover (Ch. 5.2, ADR-002)."""

from rover.domain.model import Command, Grid, Heading, Position

# Turn Left rotates the heading 90° anticlockwise (Ch. 12 Glossary)
_LEFT_OF = {
    Heading.N: Heading.W,
    Heading.W: Heading.S,
    Heading.S: Heading.E,
    Heading.E: Heading.N,
}


class Navigator:
    def apply(
        self, command: Command, position: Position, heading: Heading, grid: Grid
    ) -> tuple[Position, Heading]:
        return position, _LEFT_OF[heading]
