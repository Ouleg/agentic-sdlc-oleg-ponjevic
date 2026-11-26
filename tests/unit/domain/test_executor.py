from rover.domain.executor import CommandExecutor
from rover.domain.model import (
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
