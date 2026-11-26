import json

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from rover.main import app

scenarios("features/simulate.feature")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def context():
    return {}


@given("the Rover Service is running")
def rover_service_is_running(client):
    assert client is not None


@given(parsers.parse("a {width:d} × {height:d} grid with no obstacles"))
def a_grid_with_no_obstacles(width, height, context):
    context["grid"] = {"width": width, "height": height, "obstacles": []}


@given(
    parsers.parse("a {width:d} × {height:d} grid with one obstacle at ({x:d}, {y:d})")
)
def a_grid_with_one_obstacle(width, height, x, y, context):
    context["grid"] = {
        "width": width,
        "height": height,
        "obstacles": [{"x": x, "y": y}],
    }


@given(parsers.parse("the rover starts at ({x:d}, {y:d}) heading {heading}"))
def the_rover_starts_at(x, y, heading, context):
    context["start"] = {"x": x, "y": y, "heading": heading}


@given(parsers.parse('the Command String is "{commands}"'))
def the_command_string_is(commands, context):
    context["commands"] = commands


@when("I send POST /simulate with the JSON body")
def i_send_post_simulate(client, context, docstring):
    body = json.loads(docstring)
    assert body["grid"] == context["grid"]
    assert body["start"] == context["start"]
    if "commands" in context:
        assert body["commands"] == context["commands"]
    context["response"] = client.post("/simulate", json=body)


@when('I send POST /simulate with commands ""')
def i_send_post_simulate_with_empty_commands(client, context):
    context["response"] = client.post(
        "/simulate",
        json={"start": context["start"], "grid": context["grid"], "commands": ""},
    )


@then(parsers.parse("the response status is {status:d}"))
def the_response_status_is(context, status):
    assert context["response"].status_code == status


@then(parsers.parse("the final position is ({x:d}, {y:d})"))
def the_final_position_is(context, x, y):
    assert context["response"].json()["position"] == {"x": x, "y": y}


@then(parsers.parse("the final heading is {heading}"))
def the_final_heading_is(context, heading):
    assert context["response"].json()["heading"] == heading


@then("the blocked list is empty")
def the_blocked_list_is_empty(context):
    assert context["response"].json()["blocked"] == []


@then(parsers.parse("the blocked list is exactly {blocked}"))
def the_blocked_list_is_exactly(context, blocked):
    assert context["response"].json()["blocked"] == json.loads(blocked)


@then(
    "the F commands at indices 5 and 6 are executed after the boundary block at index 3"
)
def the_final_f_commands_are_executed(context):
    result = context["response"].json()
    assert all(entry["index"] <= 3 for entry in result["blocked"])
    assert result["position"]["x"] == 2


@then("the turns at indices 2 (L) and 5 (R) are executed between blocks")
def the_turns_between_blocks_are_executed(context):
    result = context["response"].json()
    blocked_indices = {entry["index"] for entry in result["blocked"]}
    assert 2 not in blocked_indices
    assert 5 not in blocked_indices
    assert result["heading"] == "W"
