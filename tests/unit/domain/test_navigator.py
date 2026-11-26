from rover.domain.model import Command, Grid, Heading, Position
from rover.domain.navigator import Navigator


def test_turning_left_rotates_heading_anticlockwise():
    """NAV-BE-001.1-S1"""
    # GIVEN
    grid = Grid(width=5, height=5)
    position = Position(2, 2)
    heading = Heading.N
    navigator = Navigator()

    # WHEN
    new_position, new_heading = navigator.apply(Command.L, position, heading, grid)

    # THEN
    assert new_heading == Heading.W
    assert new_position == Position(2, 2)
