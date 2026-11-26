from rover.domain.executor import CommandExecutor
from rover.domain.model import (
    BlockedMove,
    Command,
    Grid,
    Heading,
    Position,
    SimulationRequest,
    SimulationResult,
)


def test_nav_be_001_2_s1_commands_are_executed_in_order():
    """NAV-BE-001.2-S1"""
    # GIVEN
    grid = Grid(width=5, height=5)
    request = SimulationRequest(
        start=Position(0, 0),
        heading=Heading.N,
        grid=grid,
        commands=[Command.F, Command.F, Command.R, Command.F, Command.F],
    )
    executor = CommandExecutor()

    # WHEN
    result = executor.execute(request)

    # THEN
    assert result == SimulationResult(
        position=Position(2, 2), heading=Heading.E, blocked=[]
    )


def test_nav_be_001_2_s2_the_same_request_always_gives_the_same_result():
    """NAV-BE-001.2-S2"""
    # GIVEN
    request = SimulationRequest(
        start=Position(0, 0),
        heading=Heading.N,
        grid=Grid(width=5, height=5),
        commands=[Command.F, Command.F, Command.R, Command.F, Command.F],
    )
    executor = CommandExecutor()

    # WHEN
    first_result = executor.execute(request)
    second_result = executor.execute(request)

    # THEN
    assert first_result == second_result


def test_nav_be_002_2_s1_an_obstacle_block_and_a_boundary_block_are_both_accumulated():
    """NAV-BE-002.2-S1"""
    # GIVEN
    request = SimulationRequest(
        start=Position(0, 1),
        heading=Heading.E,
        grid=Grid(width=3, height=3, obstacles=frozenset({Position(1, 1)})),
        commands=[
            Command.F,
            Command.L,
            Command.F,
            Command.F,
            Command.R,
            Command.F,
            Command.F,
        ],
    )
    executor = CommandExecutor()

    # WHEN
    result = executor.execute(request)

    # THEN
    assert result.position == Position(2, 2)
    assert result.heading is Heading.E
    assert result.blocked == [
        BlockedMove(index=0, reason="obstacle"),
        BlockedMove(index=3, reason="boundary"),
    ]


def test_nav_be_002_2_s2_indices_count_all_commands_including_skipped_ones():
    """NAV-BE-002.2-S2"""
    # GIVEN
    request = SimulationRequest(
        start=Position(0, 0),
        heading=Heading.W,
        grid=Grid(width=2, height=2),
        commands=[
            Command.F,
            Command.F,
            Command.L,
            Command.F,
            Command.F,
            Command.R,
            Command.F,
            Command.F,
        ],
    )
    executor = CommandExecutor()

    # WHEN
    result = executor.execute(request)

    # THEN
    assert result.position == Position(0, 0)
    assert result.heading is Heading.W
    assert result.blocked == [
        BlockedMove(index=0, reason="boundary"),
        BlockedMove(index=1, reason="boundary"),
        BlockedMove(index=3, reason="boundary"),
        BlockedMove(index=4, reason="boundary"),
        BlockedMove(index=6, reason="boundary"),
        BlockedMove(index=7, reason="boundary"),
    ]
