from fastapi.testclient import TestClient

from rover.main import app


def test_nav_be_001_3_s1_valid_request_returns_the_simulation_result_as_json():
    """NAV-BE-001.3-S1"""
    # GIVEN
    client = TestClient(app)

    # WHEN
    response = client.post(
        "/simulate",
        json={
            "start": {"x": 0, "y": 0, "heading": "N"},
            "grid": {"width": 5, "height": 5, "obstacles": []},
            "commands": "FFRFF",
        },
    )

    # THEN
    assert response.status_code == 200
    assert response.json() == {
        "position": {"x": 2, "y": 2},
        "heading": "E",
        "blocked": [],
    }


def test_nav_be_001_3_s2_the_endpoint_is_described_in_the_generated_openapi_contract():
    """NAV-BE-001.3-S2"""
    # GIVEN
    client = TestClient(app)

    # WHEN
    response = client.get("/openapi.json")

    # THEN
    assert response.status_code == 200
    assert "post" in response.json()["paths"]["/simulate"]
