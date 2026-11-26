from rover.domain.model import Command, Grid, Heading, Position
from rover.domain.navigator import Navigator


def test_nav_be_001_1_s1_turning_left_rotates_heading_anticlockwise():
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


def test_nav_be_001_1_s2_four_right_turns_return_to_original_heading():
    """NAV-BE-001.1-S2"""
    # GIVEN
    grid = Grid(width=5, height=5)
    position = Position(2, 2)
    heading = Heading.N
    navigator = Navigator()

    # WHEN
    headings = []
    for _ in range(4):
        position, heading = navigator.apply(Command.R, position, heading, grid)
        headings.append(heading)

    # THEN
    assert headings == [Heading.E, Heading.S, Heading.W, Heading.N]
