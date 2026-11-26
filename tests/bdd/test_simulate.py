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


@given(parsers.parse("the rover starts at ({x:d}, {y:d}) heading {heading}"))
def the_rover_starts_at(x, y, heading, context):
    context["start"] = {"x": x, "y": y, "heading": heading}


@when("I send POST /simulate with the JSON body")
def i_send_post_simulate(client, context, docstring):
    body = json.loads(docstring)
    assert body["grid"] == context["grid"]
    assert body["start"] == context["start"]
    context["response"] = client.post("/simulate", json=body)


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
