from rover.domain.model import BlockedMove, Command, Grid, Heading, Position
from rover.domain.navigator import Navigator


def test_nav_be_001_1_s1_turning_left_rotates_heading_anticlockwise():
    """NAV-BE-001.1-S1"""
    # GIVEN
    grid = Grid(width=5, height=5)
    position = Position(2, 2)
    heading = Heading.N
    navigator = Navigator()

    # WHEN
    new_heading = navigator.apply(Command.L, position, heading, grid)

    # THEN
    assert new_heading == Heading.W
    assert position == Position(2, 2)


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
        heading = navigator.apply(Command.R, position, heading, grid)
        headings.append(heading)

    # THEN
    assert headings == [Heading.E, Heading.S, Heading.W, Heading.N]


def test_nav_be_001_1_s3_moving_forward_follows_the_heading():
    """NAV-BE-001.1-S3"""
    # GIVEN
    grid = Grid(width=5, height=5)
    position = Position(1, 1)
    navigator = Navigator()
    headings = [Heading.N, Heading.E, Heading.S, Heading.W]

    # WHEN
    moves = [
        navigator.apply(Command.F, position, heading, grid) for heading in headings
    ]

    # THEN
    assert moves == [
        Position(1, 2),
        Position(2, 1),
        Position(1, 0),
        Position(0, 1),
    ]
    assert headings == [Heading.N, Heading.E, Heading.S, Heading.W]


def test_nav_be_002_1_s1_forward_into_an_obstacle_is_blocked():
    """NAV-BE-002.1-S1"""
    # GIVEN
    grid = Grid(width=3, height=3, obstacles=frozenset({Position(1, 1)}))
    position = Position(0, 1)
    heading = Heading.E
    navigator = Navigator()

    # WHEN
    result = navigator.apply(Command.F, position, heading, grid)

    # THEN
    assert isinstance(result, BlockedMove)
    assert result.reason == "obstacle"
    assert position == Position(0, 1)
    assert heading is Heading.E


def test_nav_be_002_1_s2_forward_off_the_grid_is_blocked():
    """NAV-BE-002.1-S2"""
    # GIVEN
    grid = Grid(width=3, height=3)
    position = Position(0, 2)
    heading = Heading.N
    navigator = Navigator()

    # WHEN
    result = navigator.apply(Command.F, position, heading, grid)

    # THEN
    assert isinstance(result, BlockedMove)
    assert result.reason == "boundary"
    assert position == Position(0, 2)
    assert heading is Heading.N
